"""WebRTC API endpoints for direct peer-to-peer video calls."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.webrtc_service import webrtc_service
from app.models.video_conference import VideoConference
from app.models.user import User
from app.exceptions import NotFoundException, ValidationException, ForbiddenException

from app.utils.logging import logger

# Create blueprint
webrtc_bp = Blueprint('webrtc', __name__, url_prefix='/api/webrtc')


@webrtc_bp.route('/rooms', methods=['POST'])
@jwt_required()
def create_room():
    """Create a new WebRTC room."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        conference_id = data.get('conference_id')
        
        # If conference_id provided, validate it exists and user has access
        if conference_id:
            conference = VideoConference.query.get(conference_id)
            if not conference:
                return jsonify({'error': 'Conference not found'}), 404
                
            # Check if user is a participant in the conference
            user = User.query.get(current_user_id)
            is_participant = any(
                p.user_id == current_user_id 
                for p in conference.participants
            )
            
            if not is_participant and user.role not in ['admin', 'super_admin']:
                return jsonify({'error': 'Access denied'}), 403
        
        room_id = webrtc_service.create_room(conference_id)
        
        return jsonify({
            'message': 'WebRTC room created successfully',
            'room_id': room_id,
            'conference_id': conference_id,
            'join_url': f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/webrtc/{room_id}"
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating WebRTC room: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@webrtc_bp.route('/rooms/<room_id>', methods=['GET'])
@jwt_required()
def get_room_info(room_id):
    """Get WebRTC room information."""
    try:
        current_user_id = get_jwt_identity()
        
        try:
            room_info = webrtc_service.get_room_info(room_id)
        except NotFoundException as e:
            return jsonify({'error': str(e)}), 404
        
        # Check if user has access to this room
        if room_info['conference_id']:
            conference = VideoConference.query.get(room_info['conference_id'])
            if conference:
                user = User.query.get(current_user_id)
                is_participant = any(
                    p.user_id == current_user_id 
                    for p in conference.participants
                )
                
                if not is_participant and user.role not in ['admin', 'super_admin']:
                    return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'room': room_info}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting WebRTC room info: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@webrtc_bp.route('/rooms/<room_id>/join', methods=['POST'])
@jwt_required()
def join_room_api(room_id):
    """Join WebRTC room (HTTP API version)."""
    try:
        current_user_id = get_jwt_identity()
        
        # This endpoint provides room access validation
        # Actual joining happens via WebSocket
        try:
            room_info = webrtc_service.get_room_info(room_id)
        except NotFoundException as e:
            return jsonify({'error': str(e)}), 404
        
        # Check if user has access to this room
        if room_info['conference_id']:
            conference = VideoConference.query.get(room_info['conference_id'])
            if conference:
                user = User.query.get(current_user_id)
                is_participant = any(
                    p.user_id == current_user_id 
                    for p in conference.participants
                )
                
                if not is_participant and user.role not in ['admin', 'super_admin']:
                    return jsonify({'error': 'Access denied'}), 403
        
        # Get user info for frontend
        user = User.query.get(current_user_id)
        user_info = {
            'user_id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'avatar_url': getattr(user, 'avatar_url', None)
        }
        
        return jsonify({
            'message': 'Room access granted',
            'room_id': room_id,
            'user_info': user_info,
            'ice_servers': current_app.config.get('WEBRTC_ICE_SERVERS', [
                {'urls': 'stun:stun.l.google.com:19302'},
                {'urls': 'stun:stun1.l.google.com:19302'}
            ]),
            'websocket_url': current_app.config.get('WEBSOCKET_URL', 'ws://localhost:5000')
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error joining WebRTC room: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@webrtc_bp.route('/rooms/<room_id>/participants', methods=['GET'])
@jwt_required()
def get_room_participants(room_id):
    """Get WebRTC room participants."""
    try:
        current_user_id = get_jwt_identity()
        
        try:
            room_info = webrtc_service.get_room_info(room_id)
        except NotFoundException as e:
            return jsonify({'error': str(e)}), 404
        
        # Check if user has access to this room
        if room_info['conference_id']:
            conference = VideoConference.query.get(room_info['conference_id'])
            if conference:
                user = User.query.get(current_user_id)
                is_participant = any(
                    p.user_id == current_user_id 
                    for p in conference.participants
                )
                
                if not is_participant and user.role not in ['admin', 'super_admin']:
                    return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'participants': room_info['participants'],
            'participant_count': room_info['participant_count'],
            'host_id': room_info['host_id']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting room participants: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@webrtc_bp.route('/config', methods=['GET'])
@jwt_required()
def get_webrtc_config():
    """Get WebRTC configuration."""
    try:
        config = {
            'ice_servers': current_app.config.get('WEBRTC_ICE_SERVERS', [
                {'urls': 'stun:stun.l.google.com:19302'},
                {'urls': 'stun:stun1.l.google.com:19302'}
            ]),
            'websocket_url': current_app.config.get('WEBSOCKET_URL', 'ws://localhost:5000'),
            'max_participants': current_app.config.get('WEBRTC_MAX_PARTICIPANTS', 10),
            'recording_enabled': current_app.config.get('WEBRTC_RECORDING_ENABLED', True),
            'screen_sharing_enabled': current_app.config.get('WEBRTC_SCREEN_SHARING_ENABLED', True),
            'chat_enabled': current_app.config.get('WEBRTC_CHAT_ENABLED', True)
        }
        
        return jsonify({'config': config}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting WebRTC config: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@webrtc_bp.route('/rooms/<room_id>/stats', methods=['GET'])
@jwt_required()
def get_room_stats(room_id):
    """Get WebRTC room statistics."""
    try:
        current_user_id = get_jwt_identity()
        
        try:
            room_info = webrtc_service.get_room_info(room_id)
        except NotFoundException as e:
            return jsonify({'error': str(e)}), 404
        
        # Check if user has access to this room
        if room_info['conference_id']:
            conference = VideoConference.query.get(room_info['conference_id'])
            if conference:
                user = User.query.get(current_user_id)
                is_participant = any(
                    p.user_id == current_user_id 
                    for p in conference.participants
                )
                
                if not is_participant and user.role not in ['admin', 'super_admin']:
                    return jsonify({'error': 'Access denied'}), 403
        
        # Calculate room statistics
        participants = room_info['participants']
        active_participants = len([p for p in participants])
        
        # Calculate session duration
        from datetime import datetime
        created_at = datetime.fromisoformat(room_info['created_at'])
        session_duration = int((datetime.utcnow() - created_at).total_seconds() / 60)
        
        stats = {
            'room_id': room_id,
            'session_duration_minutes': session_duration,
            'active_participants': active_participants,
            'total_participants_joined': len(participants),
            'is_recording': room_info['is_recording'],
            'screen_sharing_active': room_info['screen_sharing'] is not None,
            'chat_messages': room_info['chat_message_count'],
            'created_at': room_info['created_at']
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting room stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@webrtc_bp.route('/user/active-sessions', methods=['GET'])
@jwt_required()
def get_user_active_sessions():
    """Get user's active WebRTC sessions."""
    try:
        current_user_id = get_jwt_identity()
        
        # Find rooms where user is currently participating
        active_sessions = []
        
        for room_id, room in webrtc_service.rooms.items():
            for participant_id, participant_info in room.participants.items():
                if participant_info['user_info']['user_id'] == current_user_id:
                    session_info = {
                        'room_id': room_id,
                        'participant_id': participant_id,
                        'conference_id': room.conference_id,
                        'joined_at': participant_info['joined_at'].isoformat(),
                        'is_host': participant_id == room.host_id,
                        'participant_count': len(room.participants),
                        'is_recording': room.is_recording,
                        'screen_sharing_active': room.screen_sharing is not None
                    }
                    
                    # Add conference info if available
                    if room.conference_id:
                        conference = VideoConference.query.get(room.conference_id)
                        if conference:
                            session_info['conference_title'] = conference.title
                            
                    active_sessions.append(session_info)
                    break
        
        return jsonify({
            'active_sessions': active_sessions,
            'total_active': len(active_sessions)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting user active sessions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Error handlers
@webrtc_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@webrtc_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400


@webrtc_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Access forbidden'}), 403


@webrtc_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500