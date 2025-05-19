"""Enhanced Calendar API endpoints with better error handling."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.availability import AvailabilitySchedule, AvailabilitySlot

calendar_enhanced_bp = Blueprint('calendar_enhanced', __name__)

@calendar_enhanced_bp.route('/calendar/events', methods=['GET'])
@jwt_required()
def get_calendar_events():
    """Get calendar events for the current user with enhanced error handling."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': 'User not found'
            }), 404
        
        # Get date range from query params
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        # Validate date parameters
        if not start_date or not end_date:
            return jsonify({
                'error': 'missing_parameters',
                'message': 'Start and end date parameters are required'
            }), 400
            
        try:
            # Convert strings to datetime objects
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'error': 'invalid_date_format',
                'message': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Initialize events list
        events = []
        
        # Get appointments based on user role
        if user.role == 'student' or user.role == 'trainee':
            appointments = Appointment.query.filter(
                Appointment.beneficiary_id == user.id,
                Appointment.scheduled_date.between(start, end)
            ).all()
        else:
            appointments = Appointment.query.filter(
                Appointment.trainer_id == user_id,
                Appointment.scheduled_date.between(start, end)
            ).all()
        
        # Format appointments as events
        for appointment in appointments:
            # Use scheduled_date and time instead of datetime attribute
            appointment_datetime = datetime.combine(
                appointment.scheduled_date,
                appointment.scheduled_time or datetime.min.time()
            )
            
            events.append({
                'id': str(appointment.id),
                'title': appointment.title or f"Appointment with {appointment.beneficiary.full_name if appointment.beneficiary else 'Unknown'}",
                'start': appointment_datetime.isoformat(),
                'end': (appointment_datetime + timedelta(hours=1)).isoformat(),  # Default 1 hour duration
                'type': 'appointment',
                'status': appointment.status,
                'description': appointment.notes or '',
                'beneficiary': {
                    'id': appointment.beneficiary.id,
                    'name': appointment.beneficiary.full_name
                } if appointment.beneficiary else None,
                'trainer': {
                    'id': appointment.trainer.id,
                    'name': appointment.trainer.full_name
                } if appointment.trainer else None
            })
        
        # Add availability slots for trainers
        if user.role in ['trainer', 'tenant_admin', 'super_admin']:
            schedule = AvailabilitySchedule.query.filter_by(
                user_id=user_id,
                is_active=True
            ).first()
            
            if schedule:
                slots = AvailabilitySlot.query.filter_by(schedule_id=schedule.id).all()
                
                # Create recurring availability events
                current = start
                while current <= end:
                    for slot in slots:
                        if current.weekday() == slot.day_of_week:
                            try:
                                slot_start = current.replace(
                                    hour=int(slot.start_time.split(':')[0]),
                                    minute=int(slot.start_time.split(':')[1])
                                )
                                slot_end = current.replace(
                                    hour=int(slot.end_time.split(':')[0]),
                                    minute=int(slot.end_time.split(':')[1])
                                )
                                
                                # Check if this slot is not already booked
                                is_booked = any(
                                    appointment_datetime <= slot_start < 
                                    appointment_datetime + timedelta(hours=1)
                                    for appointment in appointments
                                    for appointment_datetime in [
                                        datetime.combine(appointment.scheduled_date, 
                                                       appointment.scheduled_time or datetime.min.time())
                                    ]
                                )
                                
                                if not is_booked:
                                    events.append({
                                        'id': f'availability_{slot.id}_{current.date()}',
                                        'title': 'Available',
                                        'start': slot_start.isoformat(),
                                        'end': slot_end.isoformat(),
                                        'type': 'availability',
                                        'status': 'available',
                                        'color': 'green'
                                    })
                            except (ValueError, AttributeError) as e:
                                # Skip invalid time slots
                                continue
                    
                    current += timedelta(days=1)
        
        # Google Calendar integration check (optional)
        google_calendar_connected = False
        google_events = []
        
        # Check if user has Google Calendar connected
        # This is placeholder logic - implement actual Google Calendar check
        if hasattr(user, 'google_calendar_token') and user.google_calendar_token:
            google_calendar_connected = True
            # Fetch Google Calendar events if connected
            # google_events = fetch_google_calendar_events(user, start, end)
        
        return jsonify({
            'events': events,
            'google_calendar_connected': google_calendar_connected,
            'google_events': google_events,
            'total_events': len(events)
        }), 200
        
    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f"Calendar events error: {str(e)}")
        
        return jsonify({
            'error': 'server_error',
            'message': 'An error occurred while fetching calendar events',
            'details': str(e) if current_app.config.get('DEBUG') else None
        }), 500


@calendar_enhanced_bp.route('/calendar/availability', methods=['GET'])
@jwt_required()
def get_availability():
    """Get availability settings for the current user."""
    try:
        user_id = get_jwt_identity()
        
        schedule = AvailabilitySchedule.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        
        if not schedule:
            return jsonify({
                'schedule': None,
                'slots': [],
                'message': 'No availability schedule found'
            }), 200
        
        slots = AvailabilitySlot.query.filter_by(schedule_id=schedule.id).all()
        
        return jsonify({
            'schedule': {
                'id': schedule.id,
                'name': schedule.name,
                'is_active': schedule.is_active,
                'timezone': schedule.timezone,
                'created_at': schedule.created_at.isoformat()
            },
            'slots': [{
                'id': slot.id,
                'day_of_week': slot.day_of_week,
                'start_time': slot.start_time,
                'end_time': slot.end_time,
                'is_available': slot.is_available
            } for slot in slots]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Availability fetch error: {str(e)}")
        
        return jsonify({
            'error': 'server_error',
            'message': 'An error occurred while fetching availability',
            'details': str(e) if current_app.config.get('DEBUG') else None
        }), 500


@calendar_enhanced_bp.route('/calendar/availability', methods=['POST'])
@jwt_required()
def update_availability():
    """Update availability settings for the current user."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'No data provided'
            }), 400
        
        # Find or create schedule
        schedule = AvailabilitySchedule.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        
        if not schedule:
            schedule = AvailabilitySchedule(
                user_id=user_id,
                name=data.get('schedule_name', 'Default Schedule'),
                timezone=data.get('timezone', 'UTC'),
                is_active=True
            )
            db.session.add(schedule)
            db.session.commit()
        
        # Update or create slots
        slots_data = data.get('slots', [])
        
        for slot_data in slots_data:
            slot_id = slot_data.get('id')
            
            if slot_id:
                # Update existing slot
                slot = AvailabilitySlot.query.get(slot_id)
                if slot and slot.schedule_id == schedule.id:
                    slot.day_of_week = slot_data.get('day_of_week', slot.day_of_week)
                    slot.start_time = slot_data.get('start_time', slot.start_time)
                    slot.end_time = slot_data.get('end_time', slot.end_time)
                    slot.is_available = slot_data.get('is_available', slot.is_available)
            else:
                # Create new slot
                slot = AvailabilitySlot(
                    schedule_id=schedule.id,
                    day_of_week=slot_data.get('day_of_week'),
                    start_time=slot_data.get('start_time'),
                    end_time=slot_data.get('end_time'),
                    is_available=slot_data.get('is_available', True)
                )
                db.session.add(slot)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Availability updated successfully',
            'schedule_id': schedule.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Availability update error: {str(e)}")
        
        return jsonify({
            'error': 'server_error',
            'message': 'An error occurred while updating availability',
            'details': str(e) if current_app.config.get('DEBUG') else None
        }), 500