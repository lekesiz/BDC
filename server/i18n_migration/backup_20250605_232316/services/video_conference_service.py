"""Video Conference service implementation module."""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app

from app.extensions import db
from app.models.video_conference import (
    VideoConference, VideoConferenceParticipant, VideoConferenceRecording,
    VideoConferenceInvitation, VideoConferenceAnalytics,
    VideoConferenceProvider, VideoConferenceStatus, RecordingStatus
)
from app.models.appointment import Appointment
from app.models.user import User
from app.services.email_service import send_notification_email
from app.services.sms_service import SMSService
from app.services.notification_service import NotificationService
from app.exceptions import NotFoundException, ValidationException, ForbiddenException
from app.services.video_conference_providers import (
    VideoConferenceProviderInterface,
    ZoomProvider,
    GoogleMeetProvider,
    MicrosoftTeamsProvider,
    WebRTCProvider
)

logger = logging.getLogger(__name__)


class ZoomProvider(VideoConferenceProviderInterface):
    """Zoom video conference provider implementation."""
    
    def __init__(self):
        self.api_key = current_app.config.get('ZOOM_API_KEY')
        self.api_secret = current_app.config.get('ZOOM_API_SECRET')
        self.base_url = 'https://api.zoom.us/v2'
        self.access_token = self._get_access_token()
    
    def _get_access_token(self) -> str:
        """Get access token for Zoom API."""
        try:
            # Implementation would depend on your Zoom OAuth setup
            # This is a simplified version
            return current_app.config.get('ZOOM_ACCESS_TOKEN', '')
        except Exception as e:
            logger.error(f"Error getting Zoom access token: {str(e)}")
            return ''
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated request to Zoom API."""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            response.raise_for_status()
            return response.json() if response.content else {}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Zoom API request failed: {str(e)}")
            raise ValidationException(f"Zoom API error: {str(e)}")
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Zoom meeting."""
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
                'join_before_host': False,
                'mute_upon_entry': True,
                'watermark': False,
                'use_pmi': False,
                'approval_type': 2,
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
                'registrants_email_notification': True
            }
        }
        
        if meeting_data.get('meeting_password'):
            zoom_data['password'] = meeting_data['meeting_password']
        
        result = self._make_request('POST', '/users/me/meetings', zoom_data)
        
        return {
            'meeting_id': str(result['id']),
            'meeting_url': result['join_url'],
            'start_url': result['start_url'],
            'meeting_password': result.get('password', ''),
            'provider_data': result
        }
    
    def update_meeting(self, meeting_id: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Zoom meeting."""
        zoom_data = {
            'topic': meeting_data.get('title'),
            'start_time': meeting_data['start_time'].strftime('%Y-%m-%dT%H:%M:%SZ') if 'start_time' in meeting_data else None,
            'duration': meeting_data.get('duration_minutes'),
            'agenda': meeting_data.get('description'),
        }
        
        # Remove None values
        zoom_data = {k: v for k, v in zoom_data.items() if v is not None}
        
        result = self._make_request('PATCH', f'/meetings/{meeting_id}', zoom_data)
        return {'success': True, 'provider_data': result}
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a Zoom meeting."""
        try:
            self._make_request('DELETE', f'/meetings/{meeting_id}')
            return True
        except Exception as e:
            logger.error(f"Error deleting Zoom meeting: {str(e)}")
            return False
    
    def get_meeting_info(self, meeting_id: str) -> Dict[str, Any]:
        """Get Zoom meeting information."""
        return self._make_request('GET', f'/meetings/{meeting_id}')
    
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
            return result.get('recording_files', [])
        except Exception as e:
            logger.error(f"Error getting Zoom recordings: {str(e)}")
            return []


class GoogleMeetProvider(VideoConferenceProviderInterface):
    """Google Meet video conference provider implementation."""
    
    def __init__(self):
        self.credentials = current_app.config.get('GOOGLE_MEET_CREDENTIALS')
        self.base_url = 'https://meet.googleapis.com/v2'
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Google Meet meeting."""
        # Implementation would use Google Meet API
        # This is a placeholder implementation
        meeting_id = f"meet-{datetime.utcnow().timestamp()}"
        meeting_url = f"https://meet.google.com/{meeting_id}"
        
        return {
            'meeting_id': meeting_id,
            'meeting_url': meeting_url,
            'meeting_password': '',
            'provider_data': {'google_meet_id': meeting_id}
        }
    
    def update_meeting(self, meeting_id: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Google Meet meeting."""
        return {'success': True}
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a Google Meet meeting."""
        return True
    
    def get_meeting_info(self, meeting_id: str) -> Dict[str, Any]:
        """Get Google Meet meeting information."""
        return {'id': meeting_id, 'status': 'active'}
    
    def start_recording(self, meeting_id: str) -> bool:
        """Start recording a Google Meet meeting."""
        return True
    
    def stop_recording(self, meeting_id: str) -> bool:
        """Stop recording a Google Meet meeting."""
        return True
    
    def get_recordings(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get recordings for a Google Meet meeting."""
        return []


class MicrosoftTeamsProvider(VideoConferenceProviderInterface):
    """Microsoft Teams video conference provider implementation."""
    
    def __init__(self):
        self.client_id = current_app.config.get('TEAMS_CLIENT_ID')
        self.client_secret = current_app.config.get('TEAMS_CLIENT_SECRET')
        self.base_url = 'https://graph.microsoft.com/v1.0'
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Microsoft Teams meeting."""
        # Implementation would use Microsoft Graph API
        # This is a placeholder implementation
        meeting_id = f"teams-{datetime.utcnow().timestamp()}"
        meeting_url = f"https://teams.microsoft.com/l/meetup-join/{meeting_id}"
        
        return {
            'meeting_id': meeting_id,
            'meeting_url': meeting_url,
            'meeting_password': '',
            'provider_data': {'teams_id': meeting_id}
        }
    
    def update_meeting(self, meeting_id: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Microsoft Teams meeting."""
        return {'success': True}
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a Microsoft Teams meeting."""
        return True
    
    def get_meeting_info(self, meeting_id: str) -> Dict[str, Any]:
        """Get Microsoft Teams meeting information."""
        return {'id': meeting_id, 'status': 'active'}
    
    def start_recording(self, meeting_id: str) -> bool:
        """Start recording a Microsoft Teams meeting."""
        return True
    
    def stop_recording(self, meeting_id: str) -> bool:
        """Stop recording a Microsoft Teams meeting."""
        return True
    
    def get_recordings(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get recordings for a Microsoft Teams meeting."""
        return []


class WebRTCProvider(VideoConferenceProviderInterface):
    """WebRTC direct peer-to-peer provider implementation."""
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a WebRTC meeting room."""
        import uuid
        meeting_id = str(uuid.uuid4())
        meeting_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/webrtc/{meeting_id}"
        
        return {
            'meeting_id': meeting_id,
            'meeting_url': meeting_url,
            'meeting_password': meeting_data.get('meeting_password', ''),
            'provider_data': {
                'webrtc_room_id': meeting_id,
                'ice_servers': current_app.config.get('WEBRTC_ICE_SERVERS', [])
            }
        }
    
    def update_meeting(self, meeting_id: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a WebRTC meeting."""
        return {'success': True}
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a WebRTC meeting."""
        return True
    
    def get_meeting_info(self, meeting_id: str) -> Dict[str, Any]:
        """Get WebRTC meeting information."""
        return {'id': meeting_id, 'status': 'active'}
    
    def start_recording(self, meeting_id: str) -> bool:
        """Start recording a WebRTC meeting."""
        # Would integrate with client-side recording
        return True
    
    def stop_recording(self, meeting_id: str) -> bool:
        """Stop recording a WebRTC meeting."""
        return True
    
    def get_recordings(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get recordings for a WebRTC meeting."""
        return []


class VideoConferenceService:
    """Video Conference service for managing video conferences."""
    
    def __init__(self, notification_service: NotificationService = None, sms_service: SMSService = None):
        """Initialize video conference service."""
        self.notification_service = notification_service
        self.sms_service = sms_service
        self.providers = {
            VideoConferenceProvider.ZOOM: ZoomProvider(),
            VideoConferenceProvider.GOOGLE_MEET: GoogleMeetProvider(),
            VideoConferenceProvider.MICROSOFT_TEAMS: MicrosoftTeamsProvider(),
            VideoConferenceProvider.WEBRTC: WebRTCProvider()
        }
    
    def create_conference_for_appointment(
        self,
        appointment_id: int,
        host_id: int,
        provider: VideoConferenceProvider = VideoConferenceProvider.ZOOM,
        settings: Dict[str, Any] = None
    ) -> VideoConference:
        """
        Create a video conference for an appointment.
        
        Args:
            appointment_id: The appointment ID
            host_id: The host user ID
            provider: Video conference provider
            settings: Conference settings
            
        Returns:
            VideoConference: Created conference object
        """
        # Validate appointment
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise NotFoundException(f"Appointment {appointment_id} not found")
        
        # Validate host
        host = User.query.get(host_id)
        if not host:
            raise NotFoundException(f"Host user {host_id} not found")
        
        # Check if conference already exists
        existing_conference = VideoConference.query.filter_by(appointment_id=appointment_id).first()
        if existing_conference:
            raise ValidationException("Conference already exists for this appointment")
        
        # Prepare meeting data
        meeting_data = {
            'title': appointment.title,
            'description': appointment.description or f"Video conference for appointment: {appointment.title}",
            'start_time': appointment.start_time,
            'end_time': appointment.end_time,
            'duration_minutes': int((appointment.end_time - appointment.start_time).total_seconds() / 60),
            'waiting_room_enabled': settings.get('waiting_room_enabled', True) if settings else True,
            'require_authentication': settings.get('require_authentication', False) if settings else False,
            'auto_record': settings.get('auto_record', False) if settings else False,
            'meeting_password': settings.get('meeting_password') if settings else None
        }
        
        # Create meeting with provider
        provider_instance = self.providers[provider]
        provider_result = provider_instance.create_meeting(meeting_data)
        
        # Create conference record
        conference = VideoConference(
            appointment_id=appointment_id,
            host_id=host_id,
            title=meeting_data['title'],
            description=meeting_data['description'],
            provider=provider,
            status=VideoConferenceStatus.SCHEDULED,
            meeting_id=provider_result['meeting_id'],
            meeting_url=provider_result['meeting_url'],
            meeting_password=provider_result.get('meeting_password'),
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            duration_minutes=meeting_data['duration_minutes'],
            waiting_room_enabled=meeting_data['waiting_room_enabled'],
            require_authentication=meeting_data['require_authentication'],
            auto_record=meeting_data['auto_record'],
            provider_settings=provider_result.get('provider_data', {})
        )
        
        db.session.add(conference)
        db.session.flush()
        
        # Add participants
        participants = []
        
        # Add host as participant
        host_participant = VideoConferenceParticipant(
            conference_id=conference.id,
            user_id=host_id,
            email=host.email,
            name=f"{host.first_name} {host.last_name}",
            role='host'
        )
        participants.append(host_participant)
        
        # Add beneficiary as participant
        if appointment.beneficiary:
            beneficiary_participant = VideoConferenceParticipant(
                conference_id=conference.id,
                user_id=appointment.beneficiary.user.id,
                email=appointment.beneficiary.user.email,
                name=f"{appointment.beneficiary.user.first_name} {appointment.beneficiary.user.last_name}",
                role='participant'
            )
            participants.append(beneficiary_participant)
        
        db.session.add_all(participants)
        
        # Create analytics record
        analytics = VideoConferenceAnalytics(conference_id=conference.id)
        db.session.add(analytics)
        
        db.session.commit()
        
        # Send notifications
        self._send_conference_notifications(conference, 'created')
        
        return conference
    
    def update_conference(
        self,
        conference_id: int,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> VideoConference:
        """
        Update a video conference.
        
        Args:
            conference_id: The conference ID
            user_id: The requesting user ID
            update_data: Update data
            
        Returns:
            VideoConference: Updated conference object
        """
        conference = VideoConference.query.get(conference_id)
        if not conference:
            raise NotFoundException(f"Conference {conference_id} not found")
        
        # Check permissions
        if conference.host_id != user_id:
            user = User.query.get(user_id)
            if not user or user.role not in ['admin', 'super_admin']:
                raise ForbiddenException("You don't have permission to update this conference")
        
        # Update provider meeting if necessary
        if any(key in update_data for key in ['title', 'description', 'start_time', 'end_time']):
            provider_instance = self.providers[conference.provider]
            
            provider_update_data = {}
            if 'title' in update_data:
                provider_update_data['title'] = update_data['title']
            if 'description' in update_data:
                provider_update_data['description'] = update_data['description']
            if 'start_time' in update_data:
                provider_update_data['start_time'] = update_data['start_time']
            if 'end_time' in update_data:
                provider_update_data['end_time'] = update_data['end_time']
                if 'start_time' in update_data:
                    provider_update_data['duration_minutes'] = int(
                        (update_data['end_time'] - update_data['start_time']).total_seconds() / 60
                    )
            
            provider_instance.update_meeting(conference.meeting_id, provider_update_data)
        
        # Update local record
        for key, value in update_data.items():
            if hasattr(conference, key):
                setattr(conference, key, value)
        
        conference.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Send notifications
        self._send_conference_notifications(conference, 'updated')
        
        return conference
    
    def cancel_conference(self, conference_id: int, user_id: int) -> bool:
        """
        Cancel a video conference.
        
        Args:
            conference_id: The conference ID
            user_id: The requesting user ID
            
        Returns:
            bool: Success status
        """
        conference = VideoConference.query.get(conference_id)
        if not conference:
            raise NotFoundException(f"Conference {conference_id} not found")
        
        # Check permissions
        if conference.host_id != user_id:
            user = User.query.get(user_id)
            if not user or user.role not in ['admin', 'super_admin']:
                raise ForbiddenException("You don't have permission to cancel this conference")
        
        # Cancel with provider
        provider_instance = self.providers[conference.provider]
        provider_instance.delete_meeting(conference.meeting_id)
        
        # Update status
        conference.status = VideoConferenceStatus.CANCELLED
        conference.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Send notifications
        self._send_conference_notifications(conference, 'cancelled')
        
        return True
    
    def start_conference(self, conference_id: int, user_id: int) -> Dict[str, Any]:
        """
        Start a video conference.
        
        Args:
            conference_id: The conference ID
            user_id: The user ID starting the conference
            
        Returns:
            Dict: Conference start information
        """
        conference = VideoConference.query.get(conference_id)
        if not conference:
            raise NotFoundException(f"Conference {conference_id} not found")
        
        # Check if user is a participant
        participant = VideoConferenceParticipant.query.filter_by(
            conference_id=conference_id,
            user_id=user_id
        ).first()
        
        if not participant:
            raise ForbiddenException("You are not a participant in this conference")
        
        # Update conference status
        if conference.status == VideoConferenceStatus.SCHEDULED:
            conference.status = VideoConferenceStatus.STARTED
            conference.started_at = datetime.utcnow()
        
        # Update participant join time
        if not participant.has_joined:
            participant.has_joined = True
            participant.joined_at = datetime.utcnow()
        
        db.session.commit()
        
        return {
            'conference_id': conference.id,
            'meeting_url': conference.meeting_url,
            'meeting_id': conference.meeting_id,
            'meeting_password': conference.meeting_password,
            'provider': conference.provider.value,
            'provider_settings': conference.provider_settings
        }
    
    def end_conference(self, conference_id: int, user_id: int) -> bool:
        """
        End a video conference.
        
        Args:
            conference_id: The conference ID
            user_id: The user ID ending the conference
            
        Returns:
            bool: Success status
        """
        conference = VideoConference.query.get(conference_id)
        if not conference:
            raise NotFoundException(f"Conference {conference_id} not found")
        
        # Only host or admin can end conference
        if conference.host_id != user_id:
            user = User.query.get(user_id)
            if not user or user.role not in ['admin', 'super_admin']:
                raise ForbiddenException("You don't have permission to end this conference")
        
        # Update conference status
        conference.status = VideoConferenceStatus.ENDED
        conference.ended_at = datetime.utcnow()
        
        if conference.started_at:
            conference.actual_duration_minutes = int(
                (conference.ended_at - conference.started_at).total_seconds() / 60
            )
        
        # Update participants who haven't left
        for participant in conference.participants:
            if participant.has_joined and not participant.left_at:
                participant.left_at = datetime.utcnow()
                if participant.joined_at:
                    participant.duration_minutes = int(
                        (participant.left_at - participant.joined_at).total_seconds() / 60
                    )
        
        db.session.commit()
        
        # Send notifications
        self._send_conference_notifications(conference, 'ended')
        
        return True
    
    def add_participant(
        self,
        conference_id: int,
        email: str,
        name: str,
        role: str = 'participant',
        user_id: Optional[int] = None
    ) -> VideoConferenceParticipant:
        """
        Add a participant to a video conference.
        
        Args:
            conference_id: The conference ID
            email: Participant email
            name: Participant name
            role: Participant role
            user_id: User ID if registered user
            
        Returns:
            VideoConferenceParticipant: Created participant object
        """
        conference = VideoConference.query.get(conference_id)
        if not conference:
            raise NotFoundException(f"Conference {conference_id} not found")
        
        # Check if participant already exists
        existing_participant = VideoConferenceParticipant.query.filter_by(
            conference_id=conference_id,
            email=email
        ).first()
        
        if existing_participant:
            raise ValidationException("Participant already exists in this conference")
        
        participant = VideoConferenceParticipant(
            conference_id=conference_id,
            user_id=user_id,
            email=email,
            name=name,
            role=role
        )
        
        db.session.add(participant)
        db.session.commit()
        
        # Send invitation
        self.send_invitation(conference_id, email, name)
        
        return participant
    
    def send_invitation(
        self,
        conference_id: int,
        email: str,
        name: str,
        delivery_method: str = 'email',
        phone_number: Optional[str] = None
    ) -> VideoConferenceInvitation:
        """
        Send invitation for a video conference.
        
        Args:
            conference_id: The conference ID
            email: Recipient email
            name: Recipient name
            delivery_method: Delivery method ('email', 'sms', 'both')
            phone_number: Phone number for SMS
            
        Returns:
            VideoConferenceInvitation: Created invitation object
        """
        conference = VideoConference.query.get(conference_id)
        if not conference:
            raise NotFoundException(f"Conference {conference_id} not found")
        
        # Create invitation record
        invitation = VideoConferenceInvitation(
            conference_id=conference_id,
            email=email,
            name=name,
            role='participant',
            subject=f"Video Conference Invitation: {conference.title}",
            message=self._generate_invitation_message(conference),
            delivery_method=delivery_method,
            phone_number=phone_number
        )
        
        db.session.add(invitation)
        db.session.flush()
        
        # Send invitation
        success = False
        
        if delivery_method in ['email', 'both']:
            success = self._send_email_invitation(invitation, conference)
        
        if delivery_method in ['sms', 'both'] and phone_number:
            sms_success = self._send_sms_invitation(invitation, conference)
            success = success or sms_success
        
        # Update invitation status
        if success:
            invitation.status = 'sent'
            invitation.sent_at = datetime.utcnow()
        else:
            invitation.status = 'failed'
        
        db.session.commit()
        
        return invitation
    
    def start_recording(self, conference_id: int, user_id: int) -> VideoConferenceRecording:
        """
        Start recording a video conference.
        
        Args:
            conference_id: The conference ID
            user_id: The user ID starting the recording
            
        Returns:
            VideoConferenceRecording: Created recording object
        """
        conference = VideoConference.query.get(conference_id)
        if not conference:
            raise NotFoundException(f"Conference {conference_id} not found")
        
        # Check permissions
        if conference.host_id != user_id:
            user = User.query.get(user_id)
            if not user or user.role not in ['admin', 'super_admin']:
                raise ForbiddenException("You don't have permission to start recording")
        
        if not conference.allow_recording:
            raise ValidationException("Recording is not allowed for this conference")
        
        # Start recording with provider
        provider_instance = self.providers[conference.provider]
        success = provider_instance.start_recording(conference.meeting_id)
        
        if not success:
            raise ValidationException("Failed to start recording with provider")
        
        # Create recording record
        recording = VideoConferenceRecording(
            conference_id=conference_id,
            title=f"Recording: {conference.title}",
            status=RecordingStatus.RECORDING,
            started_at=datetime.utcnow()
        )
        
        db.session.add(recording)
        db.session.commit()
        
        return recording
    
    def stop_recording(self, recording_id: int, user_id: int) -> bool:
        """
        Stop recording a video conference.
        
        Args:
            recording_id: The recording ID
            user_id: The user ID stopping the recording
            
        Returns:
            bool: Success status
        """
        recording = VideoConferenceRecording.query.get(recording_id)
        if not recording:
            raise NotFoundException(f"Recording {recording_id} not found")
        
        conference = recording.conference
        
        # Check permissions
        if conference.host_id != user_id:
            user = User.query.get(user_id)
            if not user or user.role not in ['admin', 'super_admin']:
                raise ForbiddenException("You don't have permission to stop recording")
        
        # Stop recording with provider
        provider_instance = self.providers[conference.provider]
        success = provider_instance.stop_recording(conference.meeting_id)
        
        if success:
            recording.status = RecordingStatus.PROCESSING
            recording.ended_at = datetime.utcnow()
            
            if recording.started_at:
                recording.duration_minutes = int(
                    (recording.ended_at - recording.started_at).total_seconds() / 60
                )
            
            db.session.commit()
        
        return success
    
    def get_conference_analytics(self, conference_id: int) -> Dict[str, Any]:
        """
        Get analytics for a video conference.
        
        Args:
            conference_id: The conference ID
            
        Returns:
            Dict: Analytics data
        """
        conference = VideoConference.query.get(conference_id)
        if not conference:
            raise NotFoundException(f"Conference {conference_id} not found")
        
        analytics = VideoConferenceAnalytics.query.filter_by(conference_id=conference_id).first()
        if not analytics:
            analytics = VideoConferenceAnalytics(conference_id=conference_id)
            db.session.add(analytics)
            db.session.commit()
        
        # Calculate current metrics
        participants = conference.participants
        total_participants = len(participants)
        participants_who_joined = len([p for p in participants if p.has_joined])
        
        if participants_who_joined > 0:
            avg_duration = sum([p.duration_minutes or 0 for p in participants]) / participants_who_joined
        else:
            avg_duration = 0
        
        # Update analytics
        analytics.total_participants = total_participants
        analytics.average_duration_minutes = int(avg_duration)
        db.session.commit()
        
        return {
            'conference_id': conference_id,
            'analytics': analytics.to_dict(),
            'participants_summary': {
                'total_invited': total_participants,
                'total_joined': participants_who_joined,
                'join_rate': (participants_who_joined / total_participants * 100) if total_participants > 0 else 0
            }
        }
    
    def _send_conference_notifications(self, conference: VideoConference, action: str):
        """Send notifications for conference events."""
        if not self.notification_service:
            return
        
        # Send to all participants
        for participant in conference.participants:
            if participant.user_id:
                title = f"Video Conference {action.title()}"
                message = f"Your video conference '{conference.title}' has been {action}."
                
                if action == 'created':
                    message += f" Join at: {conference.meeting_url}"
                
                self.notification_service.create_notification(
                    user_id=participant.user_id,
                    type='video_conference',
                    title=title,
                    message=message,
                    data={
                        'conference_id': conference.id,
                        'action': action,
                        'meeting_url': conference.meeting_url
                    },
                    related_id=conference.id,
                    related_type='video_conference',
                    send_email=True
                )
    
    def _generate_invitation_message(self, conference: VideoConference) -> str:
        """Generate invitation message for a conference."""
        return f"""
You are invited to join the video conference: {conference.title}

Date & Time: {conference.start_time.strftime('%Y-%m-%d at %H:%M UTC')}
Duration: {conference.duration_minutes} minutes

Join URL: {conference.meeting_url}
{f'Meeting Password: {conference.meeting_password}' if conference.meeting_password else ''}

Host: {conference.host.first_name} {conference.host.last_name}

Please join a few minutes before the scheduled time.
        """.strip()
    
    def _send_email_invitation(self, invitation: VideoConferenceInvitation, conference: VideoConference) -> bool:
        """Send email invitation."""
        try:
            # Create a temporary user object for email service
            temp_user = type('obj', (object,), {
                'email': invitation.email,
                'first_name': invitation.name.split()[0] if invitation.name else 'Guest',
                'last_name': ' '.join(invitation.name.split()[1:]) if len(invitation.name.split()) > 1 else ''
            })
            
            send_notification_email(
                user=temp_user,
                notification={
                    'subject': invitation.subject,
                    'message': invitation.message
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error sending email invitation: {str(e)}")
            return False
    
    def _send_sms_invitation(self, invitation: VideoConferenceInvitation, conference: VideoConference) -> bool:
        """Send SMS invitation."""
        if not self.sms_service:
            return False
        
        try:
            sms_message = f"Video Conference: {conference.title}\n"
            sms_message += f"Time: {conference.start_time.strftime('%m/%d %H:%M')}\n"
            sms_message += f"Join: {conference.meeting_url}"
            
            self.sms_service.send_sms(
                phone_number=invitation.phone_number,
                message=sms_message
            )
            return True
        except Exception as e:
            logger.error(f"Error sending SMS invitation: {str(e)}")
            return False