"""Calendar availability API endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.availability import AvailabilitySchedule as Availability, AvailabilitySlot
from app.services.availability_service import AvailabilityService
from app.schemas.availability import (
    AvailabilitySchema,
    AvailabilityCreateSchema,
    AvailabilityUpdateSchema
)

calendar_availability_bp = Blueprint('calendar_availability', __name__)
availability_schema = AvailabilitySchema()
availability_list_schema = AvailabilitySchema(many=True)
availability_create_schema = AvailabilityCreateSchema()
availability_update_schema = AvailabilityUpdateSchema()


@calendar_availability_bp.route('/calendars/availability', methods=['GET'])
@jwt_required()
def get_availability():
    """Get current user's availability schedule."""
    current_user_id = get_jwt_identity()
    
    try:
        # Get user's schedules
        schedules = Availability.query.filter_by(user_id=current_user_id).all()
        
        return jsonify({
            'schedules': availability_list_schema.dump(schedules),
            'total': len(schedules)
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch availability'}), 500


@calendar_availability_bp.route('/calendars/availability', methods=['POST'])
@jwt_required()
def create_availability():
    """Create a new availability schedule."""
    current_user_id = get_jwt_identity()
    
    # Validate request data
    errors = availability_create_schema.validate(request.json)
    if errors:
        return jsonify({'errors': errors}), 400
    
    try:
        data = request.json
        data['user_id'] = current_user_id
        
        # If slots are provided, create them with the schedule
        slots = data.pop('slots', [])
        
        # Create the schedule
        schedule = Availability(**data)
        db.session.add(schedule)
        db.session.flush()
        
        # Create slots if provided
        for slot_data in slots:
            slot = AvailabilitySlot(schedule_id=schedule.id, **slot_data)
            db.session.add(slot)
        
        db.session.commit()
        
        # Get schedule with slots
        result = availability_schema.dump(schedule)
        result['slots'] = slots
        
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create availability'}), 500


@calendar_availability_bp.route('/calendars/availability/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_availability(user_id):
    """Get specific user's availability schedule (trainers can see student availability)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check permissions
    if current_user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        if user_id != current_user_id:
            return jsonify({'error': 'Unauthorized to view this user\'s availability'}), 403
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    is_available = request.args.get('is_available', type=bool)
    
    try:
        availabilities = AvailabilityService.get_user_availability(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            is_available=is_available
        )
        
        return jsonify(availability_list_schema.dump(availabilities)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to fetch availability'}), 500


@calendar_availability_bp.route('/calendars/availability/slots', methods=['POST'])
@jwt_required()
def create_availability_slot():
    """Create new availability slot."""
    current_user_id = get_jwt_identity()
    
    # Validate request data
    errors = availability_create_schema.validate(request.json)
    if errors:
        return jsonify({'errors': errors}), 400
    
    try:
        availability = AvailabilityService.create_availability(
            user_id=current_user_id,
            **request.json
        )
        
        return jsonify(availability_schema.dump(availability)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to create availability'}), 500


@calendar_availability_bp.route('/calendars/availability/<int:availability_id>', methods=['PUT'])
@jwt_required()
def update_availability(availability_id):
    """Update existing availability slot."""
    current_user_id = get_jwt_identity()
    
    # Check if availability exists and belongs to user
    availability = Availability.query.get(availability_id)
    if not availability:
        return jsonify({'error': 'Availability not found'}), 404
    
    if availability.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if current_user.role not in ['super_admin', 'tenant_admin']:
            return jsonify({'error': 'Unauthorized to update this availability'}), 403
    
    # Validate request data
    errors = availability_update_schema.validate(request.json)
    if errors:
        return jsonify({'errors': errors}), 400
    
    try:
        availability = AvailabilityService.update_availability(
            availability_id=availability_id,
            **request.json
        )
        
        return jsonify(availability_schema.dump(availability)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to update availability'}), 500


@calendar_availability_bp.route('/calendars/availability/<int:availability_id>', methods=['DELETE'])
@jwt_required()
def delete_availability(availability_id):
    """Delete availability slot."""
    current_user_id = get_jwt_identity()
    
    # Check if availability exists and belongs to user
    availability = Availability.query.get(availability_id)
    if not availability:
        return jsonify({'error': 'Availability not found'}), 404
    
    if availability.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if current_user.role not in ['super_admin', 'tenant_admin']:
            return jsonify({'error': 'Unauthorized to delete this availability'}), 403
    
    try:
        success = AvailabilityService.delete_availability(availability_id)
        if success:
            return jsonify({'message': 'Availability deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete availability'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@calendar_availability_bp.route('/calendars/availability/bulk', methods=['POST'])
@jwt_required()
def create_bulk_availability():
    """Create multiple availability slots at once."""
    current_user_id = get_jwt_identity()
    
    if not request.json or 'slots' not in request.json:
        return jsonify({'error': 'Invalid request format'}), 400
    
    slots = request.json['slots']
    if not isinstance(slots, list) or len(slots) == 0:
        return jsonify({'error': 'Slots must be a non-empty list'}), 400
    
    # Validate each slot
    for slot in slots:
        errors = availability_create_schema.validate(slot)
        if errors:
            return jsonify({'errors': errors}), 400
    
    try:
        availabilities = AvailabilityService.create_bulk_availability(
            user_id=current_user_id,
            slots=slots
        )
        
        return jsonify({
            'created': availability_list_schema.dump(availabilities),
            'count': len(availabilities)
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to create availability slots'}), 500


@calendar_availability_bp.route('/calendars/availability/check', methods=['POST'])
@jwt_required()
def check_availability():
    """Check if a user is available at a specific time."""
    current_user_id = get_jwt_identity()
    
    if not request.json:
        return jsonify({'error': 'Request body is required'}), 400
    
    user_id = request.json.get('user_id', current_user_id)
    date = request.json.get('date')
    time_slot = request.json.get('time_slot')
    
    if not date or not time_slot:
        return jsonify({'error': 'Date and time_slot are required'}), 400
    
    # Check permissions
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if current_user.role not in ['super_admin', 'tenant_admin', 'trainer']:
            return jsonify({'error': 'Unauthorized to check this user\'s availability'}), 403
    
    try:
        is_available = AvailabilityService.check_availability(
            user_id=user_id,
            date=date,
            time_slot=time_slot
        )
        
        return jsonify({
            'user_id': user_id,
            'date': date,
            'time_slot': time_slot,
            'is_available': is_available
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to check availability'}), 500


@calendar_availability_bp.route('/calendars/availability/exceptions', methods=['GET'])
@jwt_required()
def get_availability_exceptions():
    """Get user's availability exceptions."""
    current_user_id = get_jwt_identity()
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        from app.models.availability import AvailabilityException
        
        query = AvailabilityException.query.filter_by(user_id=current_user_id)
        
        if start_date:
            query = query.filter(AvailabilityException.date >= start_date)
        if end_date:
            query = query.filter(AvailabilityException.date <= end_date)
        
        exceptions = query.all()
        
        return jsonify({
            'exceptions': [exc.to_dict() for exc in exceptions],
            'total': len(exceptions)
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch exceptions'}), 500


@calendar_availability_bp.route('/calendars/availability/exceptions', methods=['POST'])
@jwt_required()
def create_availability_exception():
    """Create an availability exception."""
    current_user_id = get_jwt_identity()
    
    if not request.json:
        return jsonify({'error': 'Request body is required'}), 400
    
    try:
        from app.models.availability import AvailabilityException
        
        exception_data = request.json
        exception_data['user_id'] = current_user_id
        
        exception = AvailabilityException(**exception_data)
        db.session.add(exception)
        db.session.commit()
        
        return jsonify(exception.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create exception'}), 500