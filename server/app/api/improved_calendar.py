"""Improved calendar API with dependency injection."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime, timedelta

from app.core.improved_container import get_calendar_service
from app.services.interfaces.calendar_service_interface import ICalendarService

improved_calendar_bp = Blueprint('improved_calendar', __name__)


@improved_calendar_bp.route('/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    """Create a new appointment endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body is empty'
            }), 400
        
        # Validate required fields
        required_fields = ['title', 'start_time', 'end_time', 'trainer_id']
        for field in required_fields:
            if field not in json_data:
                return jsonify({
                    'error': 'validation_error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Parse datetime strings
        try:
            start_time = datetime.fromisoformat(json_data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(json_data['end_time'].replace('Z', '+00:00'))
        except ValueError as e:
            return jsonify({
                'error': 'validation_error',
                'message': 'Invalid datetime format. Use ISO format.'
            }), 400
        
        # Validate appointment duration
        if start_time >= end_time:
            return jsonify({
                'error': 'validation_error',
                'message': 'End time must be after start time'
            }), 400
        
        # Get calendar service through dependency injection
        calendar_service: ICalendarService = get_calendar_service()
        
        # Create appointment
        result = calendar_service.create_appointment(
            title=json_data['title'],
            start_time=start_time,
            end_time=end_time,
            trainer_id=json_data['trainer_id'],
            beneficiary_id=json_data.get('beneficiary_id'),
            student_id=json_data.get('student_id'),
            **{k: v for k, v in json_data.items() if k not in ['title', 'start_time', 'end_time', 'trainer_id', 'beneficiary_id', 'student_id']}
        )
        
        if not result:
            return jsonify({
                'error': 'creation_failed',
                'message': 'Failed to create appointment (possible scheduling conflict)'
            }), 409
        
        return jsonify(result), 201
    
    except Exception as e:
        current_app.logger.exception(f"Appointment creation error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_calendar_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    """Get appointment by ID endpoint with improved architecture."""
    try:
        # Get calendar service through dependency injection
        calendar_service: ICalendarService = get_calendar_service()
        
        # Get appointment
        appointment = calendar_service.get_appointment(appointment_id)
        
        if not appointment:
            return jsonify({
                'error': 'not_found',
                'message': 'Appointment not found'
            }), 404
        
        return jsonify(appointment), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get appointment error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_calendar_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get appointments endpoint with improved architecture."""
    try:
        # Get query parameters
        user_id = request.args.get('user_id', type=int)
        beneficiary_id = request.args.get('beneficiary_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        upcoming_only = request.args.get('upcoming_only', 'false').lower() == 'true'
        limit = request.args.get('limit', 10, type=int)
        
        # Get current user if no user_id specified
        if not user_id:
            user_id = get_jwt_identity()
        
        # Get calendar service through dependency injection
        calendar_service: ICalendarService = get_calendar_service()
        
        # Get appointments based on filters
        if upcoming_only:
            appointments = calendar_service.get_upcoming_appointments(user_id, limit)
        elif beneficiary_id:
            appointments = calendar_service.get_appointments_by_beneficiary(beneficiary_id)
        elif start_date and end_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                appointments = calendar_service.get_appointments_by_date_range(start_dt, end_dt, user_id)
            except ValueError:
                return jsonify({
                    'error': 'validation_error',
                    'message': 'Invalid date format. Use ISO format.'
                }), 400
        else:
            appointments = calendar_service.get_appointments_by_user(user_id)
        
        return jsonify({
            'appointments': appointments,
            'count': len(appointments)
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get appointments error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_calendar_bp.route('/appointments/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_appointments():
    """Get upcoming appointments endpoint with improved architecture."""
    try:
        # Get query parameters
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Get current user if no user_id specified
        if not user_id:
            user_id = get_jwt_identity()
        
        # Get calendar service through dependency injection
        calendar_service: ICalendarService = get_calendar_service()
        
        # Get upcoming appointments
        appointments = calendar_service.get_upcoming_appointments(user_id, limit)
        
        return jsonify({
            'appointments': appointments,
            'count': len(appointments)
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get upcoming appointments error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_calendar_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Update appointment endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body is empty'
            }), 400
        
        # Parse datetime strings if present
        if 'start_time' in json_data:
            try:
                json_data['start_time'] = datetime.fromisoformat(json_data['start_time'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'error': 'validation_error',
                    'message': 'Invalid start_time format. Use ISO format.'
                }), 400
        
        if 'end_time' in json_data:
            try:
                json_data['end_time'] = datetime.fromisoformat(json_data['end_time'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'error': 'validation_error',
                    'message': 'Invalid end_time format. Use ISO format.'
                }), 400
        
        # Validate appointment duration if both times are provided
        if 'start_time' in json_data and 'end_time' in json_data:
            if json_data['start_time'] >= json_data['end_time']:
                return jsonify({
                    'error': 'validation_error',
                    'message': 'End time must be after start time'
                }), 400
        
        # Get calendar service through dependency injection
        calendar_service: ICalendarService = get_calendar_service()
        
        # Update appointment
        result = calendar_service.update_appointment(appointment_id, **json_data)
        
        if not result:
            return jsonify({
                'error': 'update_failed',
                'message': 'Failed to update appointment or appointment not found'
            }), 404
        
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.exception(f"Update appointment error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_calendar_bp.route('/appointments/<int:appointment_id>/reschedule', methods=['POST'])
@jwt_required()
def reschedule_appointment(appointment_id):
    """Reschedule appointment endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body is empty'
            }), 400
        
        # Validate required fields
        required_fields = ['new_start_time', 'new_end_time']
        for field in required_fields:
            if field not in json_data:
                return jsonify({
                    'error': 'validation_error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Parse datetime strings
        try:
            new_start_time = datetime.fromisoformat(json_data['new_start_time'].replace('Z', '+00:00'))
            new_end_time = datetime.fromisoformat(json_data['new_end_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'error': 'validation_error',
                'message': 'Invalid datetime format. Use ISO format.'
            }), 400
        
        # Validate appointment duration
        if new_start_time >= new_end_time:
            return jsonify({
                'error': 'validation_error',
                'message': 'End time must be after start time'
            }), 400
        
        # Get calendar service through dependency injection
        calendar_service: ICalendarService = get_calendar_service()
        
        # Reschedule appointment
        success = calendar_service.reschedule_appointment(appointment_id, new_start_time, new_end_time)
        
        if not success:
            return jsonify({
                'error': 'reschedule_failed',
                'message': 'Failed to reschedule appointment (possible scheduling conflict)'
            }), 409
        
        return jsonify({
            'message': 'Appointment rescheduled successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Reschedule appointment error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_calendar_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_appointment(appointment_id):
    """Cancel appointment endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json() or {}
        reason = json_data.get('reason')
        
        # Get calendar service through dependency injection
        calendar_service: ICalendarService = get_calendar_service()
        
        # Cancel appointment
        success = calendar_service.cancel_appointment(appointment_id, reason)
        
        if not success:
            return jsonify({
                'error': 'cancel_failed',
                'message': 'Failed to cancel appointment or appointment not found'
            }), 404
        
        return jsonify({
            'message': 'Appointment cancelled successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Cancel appointment error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_calendar_bp.route('/appointments/<int:appointment_id>/confirm', methods=['POST'])
@jwt_required()
def confirm_appointment(appointment_id):
    """Confirm appointment endpoint with improved architecture."""
    try:
        # Get calendar service through dependency injection
        calendar_service: ICalendarService = get_calendar_service()
        
        # Confirm appointment
        success = calendar_service.confirm_appointment(appointment_id)
        
        if not success:
            return jsonify({
                'error': 'confirm_failed',
                'message': 'Failed to confirm appointment or appointment not found'
            }), 404
        
        return jsonify({
            'message': 'Appointment confirmed successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Confirm appointment error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_calendar_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    """Delete appointment endpoint with improved architecture."""
    try:
        # Get calendar service through dependency injection
        calendar_service: ICalendarService = get_calendar_service()
        
        # Delete appointment
        success = calendar_service.delete_appointment(appointment_id)
        
        if not success:
            return jsonify({
                'error': 'delete_failed',
                'message': 'Failed to delete appointment or appointment not found'
            }), 404
        
        return jsonify({
            'message': 'Appointment deleted successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Delete appointment error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_calendar_bp.route('/appointments/check-availability', methods=['POST'])
@jwt_required()
def check_availability():
    """Check availability endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body is empty'
            }), 400
        
        # Validate required fields
        required_fields = ['user_id', 'start_time', 'end_time']
        for field in required_fields:
            if field not in json_data:
                return jsonify({
                    'error': 'validation_error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Parse datetime strings
        try:
            start_time = datetime.fromisoformat(json_data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(json_data['end_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'error': 'validation_error',
                'message': 'Invalid datetime format. Use ISO format.'
            }), 400
        
        user_id = json_data['user_id']
        exclude_appointment_id = json_data.get('exclude_appointment_id')
        
        # Get calendar service through dependency injection
        calendar_service: ICalendarService = get_calendar_service()
        
        # Check availability
        is_available = calendar_service.check_availability(
            user_id, start_time, end_time, exclude_appointment_id
        )
        
        # Get conflicts if not available
        conflicts = []
        if not is_available:
            conflicts = calendar_service.get_conflicts(
                user_id, start_time, end_time, exclude_appointment_id
            )
        
        return jsonify({
            'available': is_available,
            'conflicts': conflicts,
            'conflict_count': len(conflicts)
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Check availability error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_calendar_bp.route('/appointments/schedule/<int:user_id>/<date>', methods=['GET'])
@jwt_required()
def get_user_schedule(user_id, date):
    """Get user schedule for a specific date endpoint with improved architecture."""
    try:
        # Parse date string
        try:
            schedule_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'error': 'validation_error',
                'message': 'Invalid date format. Use ISO format (YYYY-MM-DD).'
            }), 400
        
        # Get calendar service through dependency injection
        calendar_service: ICalendarService = get_calendar_service()
        
        # Get user schedule
        schedule = calendar_service.get_user_schedule(user_id, schedule_date)
        
        return jsonify({
            'schedule': schedule,
            'date': date,
            'user_id': user_id,
            'appointment_count': len(schedule)
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get user schedule error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500