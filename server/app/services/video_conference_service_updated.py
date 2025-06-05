"""Video Conference service implementation module - Updated version."""

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