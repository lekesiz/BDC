"""Availability API endpoints."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import datetime

from app.extensions import db
from app.models.user import User
from app.models.availability import AvailabilitySchedule, AvailabilitySlot, AvailabilityException
from app.services.availability_service import AvailabilityService

from app.utils.logging import logger

availability_bp = Blueprint('availability', __name__)


@availability_bp.route('/availability/schedule', methods=['GET'])
@jwt_required()
def get_availability_schedule():
    """Get the current user's availability schedule."""
    user_id = get_jwt_identity()
    
    # Get active schedule
    schedule = AvailabilitySchedule.query.filter_by(
        user_id=user_id,
        is_active=True
    ).first()
    
    if not schedule:
        # Create default schedule
        schedule = AvailabilityService.get_or_create_default_schedule(user_id)
    
    # Get slots
    slots = AvailabilitySlot.query.filter_by(schedule_id=schedule.id).all()
    
    # Format response
    response = schedule.to_dict()
    response['slots'] = [slot.to_dict() for slot in slots]
    
    return jsonify(response), 200


@availability_bp.route('/availability/schedule', methods=['PUT'])
@jwt_required()
def update_availability_schedule():
    """Update the current user's availability schedule."""
    user_id = get_jwt_identity()
    
    # Get active schedule
    schedule = AvailabilitySchedule.query.filter_by(
        user_id=user_id,
        is_active=True
    ).first()
    
    if not schedule:
        # Create default schedule
        schedule = AvailabilityService.get_or_create_default_schedule(user_id)
    
    # Update schedule
    updated_schedule = AvailabilityService.update_availability_schedule(
        schedule_id=schedule.id,
        data=request.json
    )
    
    if not updated_schedule:
        return jsonify({
            'error': 'Failed to update availability schedule'
        }), 500
    
    # Get updated slots
    slots = AvailabilitySlot.query.filter_by(schedule_id=updated_schedule.id).all()
    
    # Format response
    response = updated_schedule.to_dict()
    response['slots'] = [slot.to_dict() for slot in slots]
    
    return jsonify(response), 200


@availability_bp.route('/availability/exceptions', methods=['GET'])
@jwt_required()
def get_availability_exceptions():
    """Get the current user's availability exceptions."""
    user_id = get_jwt_identity()
    
    # Parse query parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        if start_date_str:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            # Default to current date
            start_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if end_date_str:
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            # Default to 30 days from start date
            end_date = start_date + datetime.timedelta(days=30)
    
    except ValueError:
        return jsonify({
            'error': 'Invalid date format. Use YYYY-MM-DD.'
        }), 400
    
    # Get exceptions
    exceptions = AvailabilityException.query.filter(
        AvailabilityException.user_id == user_id,
        AvailabilityException.date >= start_date,
        AvailabilityException.date <= end_date
    ).all()
    
    return jsonify({
        'exceptions': [exception.to_dict() for exception in exceptions]
    }), 200


@availability_bp.route('/availability/exceptions', methods=['POST'])
@jwt_required()
def add_availability_exception():
    """Add a new availability exception."""
    user_id = get_jwt_identity()
    
    # Add exception
    exception = AvailabilityService.add_availability_exception(
        user_id=user_id,
        data=request.json
    )
    
    if not exception:
        return jsonify({
            'error': 'Failed to add availability exception'
        }), 500
    
    return jsonify(exception.to_dict()), 201


@availability_bp.route('/availability/exceptions/<int:exception_id>', methods=['DELETE'])
@jwt_required()
def delete_availability_exception(exception_id):
    """Delete an availability exception."""
    user_id = get_jwt_identity()
    
    # Delete exception
    success = AvailabilityService.delete_availability_exception(
        exception_id=exception_id,
        user_id=user_id
    )
    
    if not success:
        return jsonify({
            'error': 'Failed to delete availability exception'
        }), 500
    
    return jsonify({
        'message': 'Availability exception deleted successfully'
    }), 200


@availability_bp.route('/availability/calendar', methods=['GET'])
@jwt_required()
def get_availability_calendar():
    """Get a calendar view of the current user's availability."""
    user_id = get_jwt_identity()
    
    # Parse query parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        if start_date_str:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            # Default to current date
            start_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if end_date_str:
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            # Default to 7 days from start date
            end_date = start_date + datetime.timedelta(days=7)
    
    except ValueError:
        return jsonify({
            'error': 'Invalid date format. Use YYYY-MM-DD.'
        }), 400
    
    # Get availability
    availability = AvailabilityService.get_user_availability(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return jsonify(availability), 200


@availability_bp.route('/availability/trainer/<int:trainer_id>', methods=['GET'])
@jwt_required()
def get_trainer_availability(trainer_id):
    """Get a trainer's availability for scheduling appointments."""
    # Parse query parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        if start_date_str:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            # Default to current date
            start_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if end_date_str:
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            # Default to 7 days from start date
            end_date = start_date + datetime.timedelta(days=7)
    
    except ValueError:
        return jsonify({
            'error': 'Invalid date format. Use YYYY-MM-DD.'
        }), 400
    
    # Verify the trainer exists
    trainer = User.query.get_or_404(trainer_id)
    
    # Get availability
    availability = AvailabilityService.get_user_availability(
        user_id=trainer_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return jsonify(availability), 200


@availability_bp.route('/availability/slots', methods=['GET'])
@jwt_required()
def get_available_slots():
    """Get available time slots for scheduling an appointment."""
    user_id = get_jwt_identity()
    
    # Parse query parameters
    trainer_id = request.args.get('trainer_id', type=int)
    date_str = request.args.get('date')
    duration = request.args.get('duration', 60, type=int)
    
    if not trainer_id:
        return jsonify({
            'error': 'trainer_id is required'
        }), 400
    
    # Verify the trainer exists
    trainer = User.query.get_or_404(trainer_id)
    
    try:
        if date_str:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        else:
            # Default to current date
            date = datetime.datetime.now()
    
    except ValueError:
        return jsonify({
            'error': 'Invalid date format. Use YYYY-MM-DD.'
        }), 400
    
    # Get available slots
    slots = AvailabilityService.get_available_slots(
        user_id=trainer_id,
        date=date,
        duration_minutes=duration
    )
    
    return jsonify({
        'trainer_id': trainer_id,
        'date': date.strftime('%Y-%m-%d'),
        'duration_minutes': duration,
        'available_slots': slots
    }), 200