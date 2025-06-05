"""Video Conference API endpoints."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from typing import Dict, Any

from app.services.video_conference_service import VideoConferenceService
from app.services.notification_service import NotificationService
from app.services.sms_service import SMSService
from app.models.video_conference import (
    VideoConference, VideoConferenceProvider, VideoConferenceParticipant,
    VideoConferenceRecording, VideoConferenceAnalytics
)
from app.models.user import User
from app.extensions import db
from app.exceptions import NotFoundException, ValidationException, ForbiddenException

from app.utils.logging import logger

# Create blueprint
video_conferences_bp = Blueprint('video_conferences', __name__, url_prefix='/api/video-conferences')

# Initialize services
notification_service = NotificationService(None)  # Will be properly injected in production
sms_service = SMSService()
video_conference_service = VideoConferenceService(notification_service, sms_service)


@video_conferences_bp.route('', methods=['POST'])
@jwt_required()
def create_conference():
    """Create a video conference for an appointment."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['appointment_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get provider (default to Zoom)
        provider_str = data.get('provider', 'zoom')
        try:
            provider = VideoConferenceProvider(provider_str)
        except ValueError:
            return jsonify({'error': 'Invalid provider'}), 400
        
        # Create conference
        conference = video_conference_service.create_conference_for_appointment(
            appointment_id=data['appointment_id'],
            host_id=current_user_id,
            provider=provider,
            settings=data.get('settings', {})
        )
        
        return jsonify({
            'message': 'Video conference created successfully',
            'conference': conference.to_dict()
        }), 201
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ValidationException as e:
        return jsonify({'error': str(e)}), 400
    except ForbiddenException as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Error creating video conference: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/<int:conference_id>', methods=['GET'])
@jwt_required()
def get_conference(conference_id):
    """Get video conference details."""
    try:
        current_user_id = get_jwt_identity()
        
        conference = VideoConference.query.get(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        # Check if user is a participant or has admin role
        user = User.query.get(current_user_id)
        is_participant = VideoConferenceParticipant.query.filter_by(
            conference_id=conference_id,
            user_id=current_user_id
        ).first() is not None
        
        if not is_participant and user.role not in ['admin', 'super_admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'conference': conference.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting video conference: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/<int:conference_id>', methods=['PUT'])
@jwt_required()
def update_conference(conference_id):
    """Update video conference."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Parse datetime fields if present
        if 'start_time' in data:
            data['start_time'] = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        if 'end_time' in data:
            data['end_time'] = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        
        conference = video_conference_service.update_conference(
            conference_id=conference_id,
            user_id=current_user_id,
            update_data=data
        )
        
        return jsonify({
            'message': 'Video conference updated successfully',
            'conference': conference.to_dict()
        }), 200
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ValidationException as e:
        return jsonify({'error': str(e)}), 400
    except ForbiddenException as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Error updating video conference: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/<int:conference_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_conference(conference_id):
    """Cancel video conference."""
    try:
        current_user_id = get_jwt_identity()
        
        success = video_conference_service.cancel_conference(
            conference_id=conference_id,
            user_id=current_user_id
        )
        
        if success:
            return jsonify({'message': 'Video conference cancelled successfully'}), 200
        else:
            return jsonify({'error': 'Failed to cancel conference'}), 400
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ForbiddenException as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Error cancelling video conference: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/<int:conference_id>/start', methods=['POST'])
@jwt_required()
def start_conference(conference_id):
    """Start/join video conference."""
    try:
        current_user_id = get_jwt_identity()
        
        conference_info = video_conference_service.start_conference(
            conference_id=conference_id,
            user_id=current_user_id
        )
        
        return jsonify({
            'message': 'Joining conference',
            'conference_info': conference_info
        }), 200
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ForbiddenException as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Error starting video conference: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/<int:conference_id>/end', methods=['POST'])
@jwt_required()
def end_conference(conference_id):
    """End video conference."""
    try:
        current_user_id = get_jwt_identity()
        
        success = video_conference_service.end_conference(
            conference_id=conference_id,
            user_id=current_user_id
        )
        
        if success:
            return jsonify({'message': 'Video conference ended successfully'}), 200
        else:
            return jsonify({'error': 'Failed to end conference'}), 400
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ForbiddenException as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Error ending video conference: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/<int:conference_id>/participants', methods=['POST'])
@jwt_required()
def add_participant(conference_id):
    """Add participant to video conference."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if user has permission to add participants
        conference = VideoConference.query.get(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        user = User.query.get(current_user_id)
        if conference.host_id != current_user_id and user.role not in ['admin', 'super_admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        participant = video_conference_service.add_participant(
            conference_id=conference_id,
            email=data['email'],
            name=data['name'],
            role=data.get('role', 'participant'),
            user_id=data.get('user_id')
        )
        
        return jsonify({
            'message': 'Participant added successfully',
            'participant': participant.to_dict()
        }), 201
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ValidationException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error adding participant: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/<int:conference_id>/participants', methods=['GET'])
@jwt_required()
def get_participants(conference_id):
    """Get conference participants."""
    try:
        current_user_id = get_jwt_identity()
        
        # Check permissions
        conference = VideoConference.query.get(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        user = User.query.get(current_user_id)
        is_participant = VideoConferenceParticipant.query.filter_by(
            conference_id=conference_id,
            user_id=current_user_id
        ).first() is not None
        
        if not is_participant and user.role not in ['admin', 'super_admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        participants = VideoConferenceParticipant.query.filter_by(
            conference_id=conference_id
        ).all()
        
        return jsonify({
            'participants': [p.to_dict() for p in participants]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting participants: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/<int:conference_id>/invite', methods=['POST'])
@jwt_required()
def send_invitation(conference_id):
    """Send invitation for video conference."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check permissions
        conference = VideoConference.query.get(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        user = User.query.get(current_user_id)
        if conference.host_id != current_user_id and user.role not in ['admin', 'super_admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        invitation = video_conference_service.send_invitation(
            conference_id=conference_id,
            email=data['email'],
            name=data['name'],
            delivery_method=data.get('delivery_method', 'email'),
            phone_number=data.get('phone_number')
        )
        
        return jsonify({
            'message': 'Invitation sent successfully',
            'invitation': invitation.to_dict()
        }), 201
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ValidationException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error sending invitation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/<int:conference_id>/recording/start', methods=['POST'])
@jwt_required()
def start_recording(conference_id):
    """Start recording video conference."""
    try:
        current_user_id = get_jwt_identity()
        
        recording = video_conference_service.start_recording(
            conference_id=conference_id,
            user_id=current_user_id
        )
        
        return jsonify({
            'message': 'Recording started successfully',
            'recording': recording.to_dict()
        }), 201
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ValidationException as e:
        return jsonify({'error': str(e)}), 400
    except ForbiddenException as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Error starting recording: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/recordings/<int:recording_id>/stop', methods=['POST'])
@jwt_required()
def stop_recording(recording_id):
    """Stop recording video conference."""
    try:
        current_user_id = get_jwt_identity()
        
        success = video_conference_service.stop_recording(
            recording_id=recording_id,
            user_id=current_user_id
        )
        
        if success:
            return jsonify({'message': 'Recording stopped successfully'}), 200
        else:
            return jsonify({'error': 'Failed to stop recording'}), 400
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ForbiddenException as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Error stopping recording: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/<int:conference_id>/recordings', methods=['GET'])
@jwt_required()
def get_recordings(conference_id):
    """Get recordings for video conference."""
    try:
        current_user_id = get_jwt_identity()
        
        # Check permissions
        conference = VideoConference.query.get(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        user = User.query.get(current_user_id)
        is_participant = VideoConferenceParticipant.query.filter_by(
            conference_id=conference_id,
            user_id=current_user_id
        ).first() is not None
        
        if not is_participant and user.role not in ['admin', 'super_admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        recordings = VideoConferenceRecording.query.filter_by(
            conference_id=conference_id
        ).all()
        
        return jsonify({
            'recordings': [r.to_dict() for r in recordings]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting recordings: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/<int:conference_id>/analytics', methods=['GET'])
@jwt_required()
def get_analytics(conference_id):
    """Get analytics for video conference."""
    try:
        current_user_id = get_jwt_identity()
        
        # Check permissions
        conference = VideoConference.query.get(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        user = User.query.get(current_user_id)
        if conference.host_id != current_user_id and user.role not in ['admin', 'super_admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        analytics = video_conference_service.get_conference_analytics(conference_id)
        
        return jsonify(analytics), 200
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_conferences(user_id):
    """Get video conferences for a user."""
    try:
        current_user_id = get_jwt_identity()
        
        # Users can only view their own conferences unless they're admin
        current_user = User.query.get(current_user_id)
        if current_user_id != user_id and current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get conferences where user is host or participant
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        # Query for conferences where user is host
        host_query = VideoConference.query.filter_by(host_id=user_id)
        
        # Query for conferences where user is participant
        participant_query = db.session.query(VideoConference).join(
            VideoConferenceParticipant
        ).filter(VideoConferenceParticipant.user_id == user_id)
        
        # Combine queries
        conferences_query = host_query.union(participant_query)
        
        if status:
            conferences_query = conferences_query.filter(
                VideoConference.status == status
            )
        
        conferences_query = conferences_query.order_by(
            VideoConference.start_time.desc()
        )
        
        # Paginate
        conferences = conferences_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'conferences': [c.to_dict() for c in conferences.items],
            'total': conferences.total,
            'pages': conferences.pages,
            'current_page': conferences.page,
            'per_page': conferences.per_page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting user conferences: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/providers', methods=['GET'])
@jwt_required()
def get_providers():
    """Get available video conference providers."""
    try:
        providers = [
            {
                'value': provider.value,
                'name': provider.value.replace('_', ' ').title(),
                'description': f"{provider.value.replace('_', ' ').title()} video conferencing"
            }
            for provider in VideoConferenceProvider
        ]
        
        return jsonify({'providers': providers}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting providers: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@video_conferences_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get video conference dashboard data."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Get user's conferences
        today = datetime.utcnow().date()
        
        # Today's conferences
        today_conferences = db.session.query(VideoConference).join(
            VideoConferenceParticipant
        ).filter(
            VideoConferenceParticipant.user_id == current_user_id,
            db.func.date(VideoConference.start_time) == today
        ).all()
        
        # Upcoming conferences (next 7 days)
        upcoming_conferences = db.session.query(VideoConference).join(
            VideoConferenceParticipant
        ).filter(
            VideoConferenceParticipant.user_id == current_user_id,
            VideoConference.start_time > datetime.utcnow(),
            VideoConference.start_time <= datetime.utcnow() + timedelta(days=7),
            VideoConference.status == 'scheduled'
        ).order_by(VideoConference.start_time.asc()).limit(5).all()
        
        # Recent recordings (if user is host or admin)
        recent_recordings = []
        if user.role in ['trainer', 'admin', 'super_admin']:
            recent_recordings = db.session.query(VideoConferenceRecording).join(
                VideoConference
            ).filter(
                VideoConference.host_id == current_user_id
            ).order_by(VideoConferenceRecording.created_at.desc()).limit(5).all()
        
        # Statistics
        total_conferences = db.session.query(VideoConference).join(
            VideoConferenceParticipant
        ).filter(VideoConferenceParticipant.user_id == current_user_id).count()
        
        hosted_conferences = VideoConference.query.filter_by(host_id=current_user_id).count()
        
        return jsonify({
            'today_conferences': [c.to_dict() for c in today_conferences],
            'upcoming_conferences': [c.to_dict() for c in upcoming_conferences],
            'recent_recordings': [r.to_dict() for r in recent_recordings],
            'statistics': {
                'total_conferences': total_conferences,
                'hosted_conferences': hosted_conferences,
                'attended_conferences': total_conferences - hosted_conferences
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Error handlers
@video_conferences_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@video_conferences_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400


@video_conferences_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Access forbidden'}), 403


@video_conferences_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500