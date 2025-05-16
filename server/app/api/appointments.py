"""Appointment API endpoints."""

from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime, timedelta

from app.extensions import db
from app.models.user import User
from app.models.integration import UserIntegration
from app.services.calendar_service import CalendarService
from app.services.email_service import send_notification_email

appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get appointments for current user."""
    from app.models.appointment import Appointment
    from app.models.beneficiary import Beneficiary
    
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    
    # Base query
    query = Appointment.query
    
    # Filter by user role
    if user.role == 'student':
        # Students see their own appointments
        beneficiary = Beneficiary.query.filter_by(user_id=user_id).first()
        if beneficiary:
            query = query.filter_by(beneficiary_id=beneficiary.id)
        else:
            return jsonify({'appointments': [], 'total': 0, 'pages': 0}), 200
    elif user.role == 'trainer':
        # Trainers see their appointments
        query = query.filter_by(trainer_id=user_id)
    # Admins see all appointments
    
    # Apply filters
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Appointment.start_time >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end + timedelta(days=1)  # Include end date
            query = query.filter(Appointment.start_time < end)
        except ValueError:
            pass
    
    if status:
        query = query.filter_by(status=status)
    
    # Order by date
    query = query.order_by(Appointment.start_time.asc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Serialize appointments
    appointments = []
    for appointment in pagination.items:
        appointment_dict = appointment.to_dict()
        
        # Include beneficiary info for trainers/admins
        if user.role != 'student' and appointment.beneficiary:
            appointment_dict['beneficiary'] = {
                'id': appointment.beneficiary.id,
                'first_name': appointment.beneficiary.user.first_name,
                'last_name': appointment.beneficiary.user.last_name,
                'email': appointment.beneficiary.user.email
            }
        
        # Include trainer info for students/admins
        if appointment.trainer:
            appointment_dict['trainer'] = {
                'id': appointment.trainer.id,
                'first_name': appointment.trainer.first_name,
                'last_name': appointment.trainer.last_name,
                'email': appointment.trainer.email
            }
        
        appointments.append(appointment_dict)
    
    return jsonify({
        'appointments': appointments,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@appointments_bp.route('/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    """Create a new appointment."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Validate user role
    if user.role not in ['trainer', 'admin', 'super_admin']:
        return jsonify({
            'error': 'unauthorized',
            'message': 'Only trainers and admins can create appointments'
        }), 403
    
    # Get and validate data
    data = request.get_json()
    required_fields = ['title', 'start_time', 'end_time', 'beneficiary_id']
    
    for field in required_fields:
        if field not in data:
            return jsonify({
                'error': 'missing_field',
                'message': f'Missing required field: {field}'
            }), 400
    
    # Parse dates
    try:
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({
            'error': 'invalid_date',
            'message': 'Invalid date format'
        }), 400
    
    # Validate dates
    if start_time >= end_time:
        return jsonify({
            'error': 'invalid_dates',
            'message': 'Start time must be before end time'
        }), 400
    
    if start_time < datetime.utcnow():
        return jsonify({
            'error': 'invalid_dates',
            'message': 'Cannot create appointments in the past'
        }), 400
    
    # Create appointment
    from app.models.appointment import Appointment
    from app.models.beneficiary import Beneficiary
    
    # Verify beneficiary exists and trainer has access
    beneficiary = Beneficiary.query.get(data['beneficiary_id'])
    if not beneficiary:
        return jsonify({
            'error': 'not_found',
            'message': 'Beneficiary not found'
        }), 404
    
    # Check permissions
    if user.role == 'trainer' and beneficiary.trainer_id != user_id:
        return jsonify({
            'error': 'forbidden',
            'message': 'You do not have access to this beneficiary'
        }), 403
    
    appointment = Appointment(
        title=data.get('title'),
        description=data.get('description'),
        location=data.get('location'),
        start_time=start_time,
        end_time=end_time,
        beneficiary_id=data['beneficiary_id'],
        trainer_id=user_id,
        status='scheduled'
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify(appointment.to_dict()), 201


@appointments_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Update an appointment."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    from app.models.appointment import Appointment
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check permissions
    if user.role == 'trainer' and appointment.trainer_id != user_id:
        return jsonify({
            'error': 'forbidden',
            'message': 'You do not have permission to update this appointment'
        }), 403
    
    # Get and validate data
    data = request.get_json()
    
    # Update allowed fields
    if 'title' in data:
        appointment.title = data['title']
    
    if 'description' in data:
        appointment.description = data['description']
    
    if 'location' in data:
        appointment.location = data['location']
    
    if 'status' in data and data['status'] in ['scheduled', 'completed', 'cancelled']:
        appointment.status = data['status']
    
    # Update dates if provided
    if 'start_time' in data:
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            appointment.start_time = start_time
        except ValueError:
            return jsonify({
                'error': 'invalid_date',
                'message': 'Invalid start time format'
            }), 400
    
    if 'end_time' in data:
        try:
            end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            appointment.end_time = end_time
        except ValueError:
            return jsonify({
                'error': 'invalid_date',
                'message': 'Invalid end time format'
            }), 400
    
    # Validate dates
    if appointment.start_time >= appointment.end_time:
        return jsonify({
            'error': 'invalid_dates',
            'message': 'Start time must be before end time'
        }), 400
    
    db.session.commit()
    
    return jsonify(appointment.to_dict()), 200


@appointments_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    """Delete an appointment."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    from app.models.appointment import Appointment
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check permissions
    if user.role not in ['admin', 'super_admin']:
        if user.role == 'trainer' and appointment.trainer_id != user_id:
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to delete this appointment'
            }), 403
    
    # Delete from Google Calendar if synced
    if appointment.calendar_event_id:
        integration = UserIntegration.query.filter_by(
            user_id=user_id,
            provider='google_calendar',
            status='active'
        ).first()
        
        if integration:
            CalendarService.delete_calendar_event(
                user_id=user_id,
                event_id=appointment.calendar_event_id
            )
    
    db.session.delete(appointment)
    db.session.commit()
    
    return jsonify({
        'message': 'Appointment deleted successfully'
    }), 200


@appointments_bp.route('/calendar/authorize', methods=['GET'])
@jwt_required()
def authorize_google_calendar():
    """Authorize Google Calendar integration."""
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
    # Get the authorization code and state
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or not state:
        return jsonify({
            'error': 'invalid_callback',
            'message': 'Invalid callback parameters'
        }), 400
    
    # Get the user ID from the state
    # In a real application, you would decode the state or use a session
    # For this example, we'll get the user from the integration record
    integration = UserIntegration.query.filter_by(
        status='pending',
        provider='google_calendar'
    ).first()
    
    if not integration:
        return jsonify({
            'error': 'integration_not_found',
            'message': 'Integration not found'
        }), 404
    
    user_id = integration.user_id
    
    # Handle the callback
    success = CalendarService.handle_callback(user_id, code, state)
    
    if not success:
        return jsonify({
            'error': 'callback_failed',
            'message': 'Callback handling failed'
        }), 500
    
    # Redirect to the frontend callback URL
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
    callback_url = f"{frontend_url}/settings/integrations/google-calendar/callback?success=true"
    
    return redirect(callback_url)


@appointments_bp.route('/calendar/status', methods=['GET'])
@jwt_required()
def get_calendar_integration_status():
    """Get the status of Google Calendar integration."""
    user_id = get_jwt_identity()
    
    integration = UserIntegration.query.filter_by(
        user_id=user_id,
        provider='google_calendar'
    ).first()
    
    if not integration:
        return jsonify({
            'status': 'not_connected'
        }), 200
    
    return jsonify({
        'status': integration.status,
        'connected_at': integration.updated_at.isoformat() if integration.status == 'active' else None
    }), 200


@appointments_bp.route('/calendar/disconnect', methods=['POST'])
@jwt_required()
def disconnect_google_calendar():
    """Disconnect Google Calendar integration."""
    user_id = get_jwt_identity()
    
    integration = UserIntegration.query.filter_by(
        user_id=user_id,
        provider='google_calendar'
    ).first()
    
    if not integration:
        return jsonify({
            'message': 'Integration not found'
        }), 404
    
    db.session.delete(integration)
    db.session.commit()
    
    return jsonify({
        'message': 'Google Calendar disconnected successfully'
    }), 200


@appointments_bp.route('/calendar/events', methods=['GET'])
@jwt_required()
def get_calendar_events():
    """Get calendar events."""
    user_id = get_jwt_identity()
    
    # Check if the user has an active integration
    integration = UserIntegration.query.filter_by(
        user_id=user_id,
        provider='google_calendar',
        status='active'
    ).first()
    
    if not integration:
        return jsonify({
            'error': 'not_connected',
            'message': 'Google Calendar not connected'
        }), 400
    
    # Parse query parameters
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    max_results = request.args.get('max_results', 10, type=int)
    
    # Parse dates
    start_time = None
    end_time = None
    
    if start_time_str:
        try:
            start_time = datetime.datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'error': 'invalid_date',
                'message': 'Invalid start_time format'
            }), 400
    
    if end_time_str:
        try:
            end_time = datetime.datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'error': 'invalid_date',
                'message': 'Invalid end_time format'
            }), 400
    
    # Get the events
    events = CalendarService.get_calendar_events(
        user_id=user_id,
        start_time=start_time,
        end_time=end_time,
        max_results=max_results
    )
    
    if events is None:
        return jsonify({
            'error': 'events_retrieval_failed',
            'message': 'Failed to retrieve events'
        }), 500
    
    return jsonify({
        'events': events
    }), 200


@appointments_bp.route('/appointments/<int:appointment_id>/sync', methods=['POST'])
@jwt_required()
def sync_appointment_to_calendar(appointment_id):
    """Sync an appointment to Google Calendar."""
    user_id = get_jwt_identity()
    
    # Check if the user has an active integration
    integration = UserIntegration.query.filter_by(
        user_id=user_id,
        provider='google_calendar',
        status='active'
    ).first()
    
    if not integration:
        return jsonify({
            'error': 'not_connected',
            'message': 'Google Calendar not connected'
        }), 400
    
    # Get the appointment
    from app.models.appointment import Appointment
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check permissions
    if appointment.trainer_id != user_id and not User.query.get(user_id).role in ['super_admin', 'tenant_admin']:
        return jsonify({
            'error': 'not_authorized',
            'message': 'Not authorized to sync this appointment'
        }), 403
    
    # Get the beneficiary
    beneficiary = appointment.beneficiary
    
    # Prepare the appointment data
    appointment_data = {
        'title': f"Meeting with {beneficiary.first_name} {beneficiary.last_name}",
        'description': appointment.description or f"Scheduled appointment with {beneficiary.first_name} {beneficiary.last_name}",
        'start_time': appointment.start_time,
        'end_time': appointment.end_time,
        'location': appointment.location,
        'attendees': [beneficiary.email]
    }
    
    # Create or update the event
    if appointment.calendar_event_id:
        # Update existing event
        success = CalendarService.update_calendar_event(
            user_id=user_id,
            event_id=appointment.calendar_event_id,
            appointment=appointment_data
        )
        
        if not success:
            return jsonify({
                'error': 'event_update_failed',
                'message': 'Failed to update calendar event'
            }), 500
    else:
        # Create new event
        event_id = CalendarService.create_calendar_event(
            user_id=user_id,
            appointment=appointment_data
        )
        
        if not event_id:
            return jsonify({
                'error': 'event_creation_failed',
                'message': 'Failed to create calendar event'
            }), 500
        
        # Update appointment with event ID
        appointment.calendar_event_id = event_id
        db.session.commit()
    
    # Notify the beneficiary
    send_notification_email(
        user=beneficiary,
        notification={
            'subject': f"Appointment with {appointment.trainer.first_name} {appointment.trainer.last_name}",
            'message': f"You have a scheduled appointment with {appointment.trainer.first_name} {appointment.trainer.last_name} on {appointment.start_time.strftime('%Y-%m-%d at %H:%M')}."
        }
    )
    
    return jsonify({
        'message': 'Appointment synced to Google Calendar successfully',
        'calendar_event_id': appointment.calendar_event_id
    }), 200


@appointments_bp.route('/appointments/<int:appointment_id>/unsync', methods=['POST'])
@jwt_required()
def unsync_appointment_from_calendar(appointment_id):
    """Unsync an appointment from Google Calendar."""
    user_id = get_jwt_identity()
    
    # Get the appointment
    from app.models.appointment import Appointment
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check permissions
    if appointment.trainer_id != user_id and not User.query.get(user_id).role in ['super_admin', 'tenant_admin']:
        return jsonify({
            'error': 'not_authorized',
            'message': 'Not authorized to unsync this appointment'
        }), 403
    
    # Check if the appointment has a calendar event
    if not appointment.calendar_event_id:
        return jsonify({
            'message': 'Appointment is not synced to Google Calendar'
        }), 200
    
    # Check if the user has an active integration
    integration = UserIntegration.query.filter_by(
        user_id=user_id,
        provider='google_calendar',
        status='active'
    ).first()
    
    if integration:
        # Delete the event
        success = CalendarService.delete_calendar_event(
            user_id=user_id,
            event_id=appointment.calendar_event_id
        )
        
        if not success:
            current_app.logger.warning(f"Failed to delete calendar event {appointment.calendar_event_id}")
    
    # Update appointment
    appointment.calendar_event_id = None
    db.session.commit()
    
    return jsonify({
        'message': 'Appointment unsynced from Google Calendar successfully'
    }), 200