"""Appointment API endpoints."""

from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime, timedelta

from app.extensions import db
from app.services.appointment_service_factory import AppointmentServiceFactory
from app.exceptions import NotFoundException, ForbiddenException, ValidationException

appointments_bp = Blueprint('appointments', __name__)

# Create service instance
appointment_service = AppointmentServiceFactory.create()


@appointments_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get appointments for current user."""
    try:
        user_id = get_jwt_identity()
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        
        result = appointment_service.get_appointments_for_user(
            user_id=user_id,
            page=page,
            per_page=per_page,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        
        return jsonify(result), 200
        
    except NotFoundException as e:
        return jsonify({
            'error': 'not_found',
            'message': str(e)
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error getting appointments: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Failed to get appointments'
        }), 500


@appointments_bp.route('/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    """Create a new appointment."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        appointment = appointment_service.create_appointment(
            trainer_id=user_id,
            appointment_data=data
        )
        
        return jsonify(appointment), 201
        
    except ValidationException as e:
        return jsonify({
            'error': 'validation_error',
            'message': str(e)
        }), 400
    except ForbiddenException as e:
        return jsonify({
            'error': 'forbidden',
            'message': str(e)
        }), 403
    except NotFoundException as e:
        return jsonify({
            'error': 'not_found',
            'message': str(e)
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error creating appointment: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Failed to create appointment'
        }), 500


@appointments_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Update an appointment."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        appointment = appointment_service.update_appointment(
            appointment_id=appointment_id,
            user_id=user_id,
            update_data=data
        )
        
        return jsonify(appointment), 200
        
    except ValidationException as e:
        return jsonify({
            'error': 'validation_error',
            'message': str(e)
        }), 400
    except ForbiddenException as e:
        return jsonify({
            'error': 'forbidden',
            'message': str(e)
        }), 403
    except NotFoundException as e:
        return jsonify({
            'error': 'not_found',
            'message': str(e)
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error updating appointment: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Failed to update appointment'
        }), 500


@appointments_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    """Delete an appointment."""
    try:
        user_id = get_jwt_identity()
        
        result = appointment_service.delete_appointment(
            appointment_id=appointment_id,
            user_id=user_id
        )
        
        return jsonify(result), 200
        
    except ForbiddenException as e:
        return jsonify({
            'error': 'forbidden',
            'message': str(e)
        }), 403
    except NotFoundException as e:
        return jsonify({
            'error': 'not_found',
            'message': str(e)
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting appointment: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Failed to delete appointment'
        }), 500


@appointments_bp.route('/appointments/<int:appointment_id>/sync', methods=['POST'])
@jwt_required()
def sync_appointment_to_calendar(appointment_id):
    """Sync appointment to Google Calendar."""
    try:
        user_id = get_jwt_identity()
        
        result = appointment_service.sync_to_calendar(
            appointment_id=appointment_id,
            user_id=user_id
        )
        
        return jsonify(result), 200
        
    except ValidationException as e:
        return jsonify({
            'error': 'validation_error',
            'message': str(e)
        }), 400
    except ForbiddenException as e:
        return jsonify({
            'error': 'forbidden',
            'message': str(e)
        }), 403
    except NotFoundException as e:
        return jsonify({
            'error': 'not_found',
            'message': str(e)
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error syncing appointment: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Failed to sync appointment'
        }), 500


@appointments_bp.route('/appointments/<int:appointment_id>/unsync', methods=['POST'])
@jwt_required()
def unsync_appointment_from_calendar(appointment_id):
    """Remove appointment from Google Calendar."""
    try:
        user_id = get_jwt_identity()
        
        result = appointment_service.unsync_from_calendar(
            appointment_id=appointment_id,
            user_id=user_id
        )
        
        return jsonify(result), 200
        
    except ForbiddenException as e:
        return jsonify({
            'error': 'forbidden',
            'message': str(e)
        }), 403
    except NotFoundException as e:
        return jsonify({
            'error': 'not_found',
            'message': str(e)
        }), 404
    except Exception as e:
        current_app.logger.error(f"Error unsyncing appointment: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Failed to unsync appointment'
        }), 500


# Keep existing calendar authorization endpoints as they don't need refactoring
@appointments_bp.route('/calendar/authorize', methods=['GET'])
@jwt_required()
def authorize_google_calendar():
    """Authorize Google Calendar integration."""
    from app.models.user import User
    from app.services.calendar_service import CalendarService
    
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the redirect URI
    redirect_uri = url_for('appointments.oauth2callback', _external=True)
    
    # Get the authorization URL
    authorization_url = CalendarService.get_authorization_url(user_id, redirect_uri)
    
    if not authorization_url:
        return jsonify({
            'error': 'authorization_failed',
            'message': 'Authorization failed'
        }), 500
    
    return jsonify({
        'authorization_url': authorization_url
    }), 200


@appointments_bp.route('/calendar/callback', methods=['GET'])
def oauth2callback():
    """Handle Google OAuth callback."""
    from app.services.calendar_service import CalendarService
    
    # Get the authorization code and state
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or not state:
        return jsonify({
            'error': 'invalid_callback',
            'message': 'Invalid callback parameters'
        }), 400
    
    # Complete the authorization
    success = CalendarService.handle_callback(code, state)
    
    if not success:
        return jsonify({
            'error': 'authorization_failed',
            'message': 'Failed to complete authorization'
        }), 500
    
    # Redirect to the frontend
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
    return redirect(f"{frontend_url}/settings/integrations?success=true")


@appointments_bp.route('/calendar/disconnect', methods=['POST'])
@jwt_required()
def disconnect_google_calendar():
    """Disconnect Google Calendar integration."""
    from app.models.integration import UserIntegration
    from app.services.calendar_service import CalendarService
    
    user_id = get_jwt_identity()
    
    # Revoke access
    success = CalendarService.revoke_access(user_id)
    
    # Update the integration status
    integration = UserIntegration.query.filter_by(
        user_id=user_id,
        provider='google_calendar'
    ).first()
    
    if integration:
        integration.status = 'inactive'
        integration.access_token = None
        integration.refresh_token = None
        integration.expires_at = None
        db.session.commit()
    
    return jsonify({
        'message': 'Google Calendar disconnected successfully'
    }), 200