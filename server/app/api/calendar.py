"""Calendar API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.availability import AvailabilitySchedule, AvailabilitySlot

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar/events', methods=['GET'])
@jwt_required()
def get_calendar_events():
    """Get calendar events for the current user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get date range from query params
    start_date = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
    end_date = request.args.get('end', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
    
    # Convert strings to datetime objects
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get appointments based on user role
    if user.role == 'trainee':
        appointments = Appointment.query.filter(
            Appointment.beneficiary_id == user.id,
            Appointment.datetime.between(start, end)
        ).all()
    else:
        appointments = Appointment.query.filter(
            Appointment.trainer_id == user_id,
            Appointment.datetime.between(start, end)
        ).all()
    
    # Format events for calendar
    events = []
    for appointment in appointments:
        events.append({
            'id': appointment.id,
            'title': appointment.title,
            'start': appointment.datetime.isoformat(),
            'end': (appointment.datetime + timedelta(hours=appointment.duration)).isoformat(),
            'type': appointment.appointment_type,
            'status': appointment.status,
            'description': appointment.description,
            'beneficiary': {
                'id': appointment.beneficiary.id,
                'name': f"{appointment.beneficiary.first_name} {appointment.beneficiary.last_name}"
            } if appointment.beneficiary else None,
            'trainer': {
                'id': appointment.trainer.id,
                'name': f"{appointment.trainer.first_name} {appointment.trainer.last_name}"
            } if appointment.trainer else None
        })
    
    # Add availability slots
    if user.role in ['trainer', 'tenant_admin']:
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
                            appointment.datetime <= slot_start < 
                            appointment.datetime + timedelta(hours=appointment.duration)
                            for appointment in appointments
                        )
                        
                        if not is_booked:
                            events.append({
                                'id': f'availability_{slot.id}_{current.date()}',
                                'title': 'Available',
                                'start': slot_start.isoformat(),
                                'end': slot_end.isoformat(),
                                'type': 'availability',
                                'status': 'available',
                                'backgroundColor': '#10b981'
                            })
                
                current += timedelta(days=1)
    
    return jsonify({
        'events': events,
        'total': len(events)
    }), 200


@calendar_bp.route('/calendar/events', methods=['POST'])
@jwt_required()
def create_calendar_event():
    """Create a new calendar event (appointment)."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    try:
        appointment = Appointment(
            title=data['title'],
            description=data.get('description'),
            appointment_type=data.get('type', 'meeting'),
            datetime=datetime.fromisoformat(data['start']),
            duration=data.get('duration', 1),
            trainer_id=user_id if user.role == 'trainer' else data.get('trainer_id'),
            beneficiary_id=data.get('beneficiary_id'),
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'id': appointment.id,
            'title': appointment.title,
            'start': appointment.datetime.isoformat(),
            'end': (appointment.datetime + timedelta(hours=appointment.duration)).isoformat(),
            'type': appointment.appointment_type,
            'status': appointment.status,
            'message': 'Event created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@calendar_bp.route('/calendar/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_calendar_event(event_id):
    """Update a calendar event."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    appointment = Appointment.query.get_or_404(event_id)
    
    # Check permissions
    if appointment.trainer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update appointment
    appointment.title = data.get('title', appointment.title)
    appointment.description = data.get('description', appointment.description)
    appointment.datetime = datetime.fromisoformat(data['start']) if 'start' in data else appointment.datetime
    appointment.duration = data.get('duration', appointment.duration)
    appointment.status = data.get('status', appointment.status)
    
    db.session.commit()
    
    return jsonify({
        'id': appointment.id,
        'title': appointment.title,
        'start': appointment.datetime.isoformat(),
        'end': (appointment.datetime + timedelta(hours=appointment.duration)).isoformat(),
        'type': appointment.appointment_type,
        'status': appointment.status,
        'message': 'Event updated successfully'
    }), 200


@calendar_bp.route('/calendar/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_calendar_event(event_id):
    """Delete a calendar event."""
    user_id = get_jwt_identity()
    
    appointment = Appointment.query.get_or_404(event_id)
    
    # Check permissions
    if appointment.trainer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(appointment)
    db.session.commit()
    
    return jsonify({'message': 'Event deleted successfully'}), 200