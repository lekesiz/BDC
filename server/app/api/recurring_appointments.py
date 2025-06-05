"""Recurring appointments API module."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import RecurringAppointmentService
from app.decorators import role_required
from app.extensions import db
from app.utils.datetime_utils import parse_datetime

from app.utils.logging import logger

bp = Blueprint('recurring_appointments', __name__, url_prefix='/api/recurring-appointments')


@bp.route('', methods=['POST'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def create_recurring_appointment():
    """Create a new recurring appointment series."""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Extract pattern data
        pattern_data = {
            'frequency': data.get('frequency', 'weekly'),
            'interval': data.get('interval', 1),
            'days_of_week': data.get('days_of_week'),
            'day_of_month': data.get('day_of_month'),
            'week_of_month': data.get('week_of_month'),
            'day_of_week_month': data.get('day_of_week_month'),
            'end_type': data.get('end_type', 'never'),
            'occurrences': data.get('occurrences'),
            'end_date': data.get('end_date')
        }
        
        # Create series
        series, error = RecurringAppointmentService.create_recurring_appointment(
            trainer_id=data.get('trainer_id', current_user_id),
            beneficiary_id=data['beneficiary_id'],
            title=data['title'],
            pattern_data=pattern_data,
            start_date=parse_datetime(data['start_date']),
            duration_minutes=data.get('duration_minutes', 60),
            description=data.get('description'),
            location=data.get('location')
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Recurring appointment series created successfully',
            'series': series.to_dict()
        }), 201
        
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:series_id>', methods=['GET'])
@jwt_required()
def get_series(series_id):
    """Get recurring appointment series details."""
    from app.models import AppointmentSeries
    
    series = AppointmentSeries.query.get_or_404(series_id)
    
    # Get upcoming occurrences
    upcoming = RecurringAppointmentService.get_upcoming_occurrences(series_id, limit=10)
    
    return jsonify({
        'series': series.to_dict(),
        'upcoming_occurrences': upcoming
    })


@bp.route('/<int:series_id>', methods=['PUT'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def update_series(series_id):
    """Update a recurring appointment series."""
    try:
        data = request.get_json()
        update_future_only = data.get('update_future_only', True)
        from_date = parse_datetime(data['from_date']) if data.get('from_date') else None
        
        # Remove control fields from updates
        updates = {k: v for k, v in data.items() 
                  if k not in ['update_future_only', 'from_date']}
        
        success, error = RecurringAppointmentService.update_series(
            series_id,
            updates,
            update_future_only,
            from_date
        )
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'message': 'Series updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:series_id>/pattern', methods=['PUT'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def update_pattern(series_id):
    """Update the recurrence pattern."""
    try:
        data = request.get_json()
        regenerate = data.get('regenerate', True)
        
        # Extract pattern updates
        pattern_updates = {k: v for k, v in data.items() if k != 'regenerate'}
        
        success, error = RecurringAppointmentService.update_pattern(
            series_id,
            pattern_updates,
            regenerate
        )
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'message': 'Pattern updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:series_id>/exceptions', methods=['POST'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def add_exception(series_id):
    """Add an exception date to the series."""
    try:
        data = request.get_json()
        exception_date = parse_datetime(data['exception_date'])
        
        success, error = RecurringAppointmentService.add_exception(
            series_id,
            exception_date
        )
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'message': 'Exception added successfully'})
        
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:series_id>/exceptions', methods=['DELETE'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def remove_exception(series_id):
    """Remove an exception date from the series."""
    try:
        data = request.get_json()
        exception_date = parse_datetime(data['exception_date'])
        
        success, error = RecurringAppointmentService.remove_exception(
            series_id,
            exception_date
        )
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'message': 'Exception removed successfully'})
        
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def update_single_occurrence(appointment_id):
    """Update a single occurrence without affecting the series."""
    try:
        data = request.get_json()
        
        success, error = RecurringAppointmentService.update_single_occurrence(
            appointment_id,
            data
        )
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'message': 'Appointment updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:series_id>/cancel', methods=['POST'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def cancel_series(series_id):
    """Cancel all future appointments in a series."""
    try:
        data = request.get_json()
        from_date = parse_datetime(data['from_date']) if data.get('from_date') else None
        reason = data.get('reason')
        
        count, error = RecurringAppointmentService.cancel_series(
            series_id,
            from_date,
            reason
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': f'Successfully cancelled {count} appointments',
            'cancelled_count': count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:series_id>/generate', methods=['POST'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def generate_more_occurrences(series_id):
    """Generate more occurrences for a series."""
    try:
        data = request.get_json()
        months_ahead = data.get('months_ahead', 3)
        
        count, error = RecurringAppointmentService.generate_more_occurrences(
            series_id,
            months_ahead
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': f'Successfully generated {count} new appointments',
            'created_count': count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/check-conflicts', methods=['POST'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def check_conflicts():
    """Check for scheduling conflicts."""
    try:
        data = request.get_json()
        
        conflicts = RecurringAppointmentService.check_conflicts(
            trainer_id=data['trainer_id'],
            start_date=parse_datetime(data['start_date']),
            pattern_data=data['pattern'],
            duration_minutes=data.get('duration_minutes', 60),
            exclude_series_id=data.get('exclude_series_id')
        )
        
        return jsonify({
            'conflicts': conflicts,
            'has_conflicts': len(conflicts) > 0
        })
        
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500