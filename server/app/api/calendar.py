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
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
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
                Appointment.start_time.between(start, end)
            ).all()
        else:
            appointments = Appointment.query.filter(
                Appointment.trainer_id == user_id,
                Appointment.start_time.between(start, end)
            ).all()
        
        # Format events for calendar
        events = []
        for appointment in appointments:
            events.append({
                'id': appointment.id,
                'title': appointment.title,
                'start': appointment.start_time.isoformat(),
                'end': appointment.end_time.isoformat(),
                'type': 'appointment',
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
                                appointment.start_time <= slot_start < appointment.end_time
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
        })
    except Exception as e:
        print(f"Calendar error: {str(e)}")
        return jsonify({'message': str(e)}), 400


@calendar_bp.route('/calendar/events', methods=['POST'])
@jwt_required()
def create_calendar_event():
    """Create a new calendar event."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'datetime', 'duration', 'appointment_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} is required'}), 400
    
    # Create appointment
    appointment = Appointment(
        title=data['title'],
        datetime=datetime.fromisoformat(data['datetime']),
        duration=data['duration'],
        appointment_type=data['appointment_type'],
        description=data.get('description', ''),
        location=data.get('location', ''),
        trainer_id=user_id,
        beneficiary_id=data.get('beneficiary_id')
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({
        'message': 'Appointment created successfully',
        'id': appointment.id
    }), 201


@calendar_bp.route('/calendar/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_calendar_event(event_id):
    """Update an existing calendar event."""
    user_id = get_jwt_identity()
    appointment = Appointment.query.get(event_id)
    
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    # Check if user has permission to update
    if appointment.trainer_id != user_id:
        return jsonify({'message': 'Permission denied'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'title' in data:
        appointment.title = data['title']
    if 'datetime' in data:
        appointment.datetime = datetime.fromisoformat(data['datetime'])
    if 'duration' in data:
        appointment.duration = data['duration']
    if 'appointment_type' in data:
        appointment.appointment_type = data['appointment_type']
    if 'description' in data:
        appointment.description = data['description']
    if 'location' in data:
        appointment.location = data['location']
    if 'status' in data:
        appointment.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Appointment updated successfully'
    })


@calendar_bp.route('/calendar/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_calendar_event(event_id):
    """Delete a calendar event."""
    user_id = get_jwt_identity()
    appointment = Appointment.query.get(event_id)
    
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    # Check if user has permission to delete
    if appointment.trainer_id != user_id:
        return jsonify({'message': 'Permission denied'}), 403
    
    db.session.delete(appointment)
    db.session.commit()
    
    return jsonify({
        'message': 'Appointment deleted successfully'
    })


@calendar_bp.route('/calendar/availability', methods=['GET'])
@jwt_required()
def get_availability():
    """Get availability schedule."""
    user_id = get_jwt_identity()
    
    schedule = AvailabilitySchedule.query.filter_by(
        user_id=user_id,
        is_active=True
    ).first()
    
    if not schedule:
        return jsonify({
            'schedule': None,
            'slots': []
        })
    
    slots = AvailabilitySlot.query.filter_by(schedule_id=schedule.id).all()
    
    return jsonify({
        'schedule': {
            'id': schedule.id,
            'name': schedule.name,
            'is_active': schedule.is_active,
            'created_at': schedule.created_at.isoformat()
        },
        'slots': [{
            'id': slot.id,
            'day_of_week': slot.day_of_week,
            'start_time': slot.start_time,
            'end_time': slot.end_time,
            'is_active': slot.is_active
        } for slot in slots]
    })