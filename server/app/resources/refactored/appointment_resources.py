"""Refactored appointment API endpoints with dependency injection."""

from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.container import inject
from app.services.interfaces.appointment_service_interface import IAppointmentService
from app.core.logging import get_logger

logger = get_logger(__name__)


class AppointmentListResource(Resource):
    """Resource for listing and creating appointments."""
    
    @jwt_required()
    @inject('appointment_service')
    def get(self, service: IAppointmentService):
        """Get paginated appointments."""
        try:
            user_id = get_jwt_identity()
            
            # Get query parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            status = request.args.get('status')
            
            logger.info(f"Fetching appointments for user {user_id} with filters: "
                       f"page={page}, per_page={per_page}, start_date={start_date}, "
                       f"end_date={end_date}, status={status}")
            
            result = service.get_appointments(
                user_id=user_id,
                page=page,
                per_page=per_page,
                start_date=start_date,
                end_date=end_date,
                status=status
            )
            
            return make_response(jsonify(result), 200)
            
        except Exception as e:
            logger.error(f"Error fetching appointments: {str(e)}")
            return make_response(jsonify({'error': str(e)}), 500)
    
    @jwt_required()
    @inject('appointment_service')
    def post(self, service: IAppointmentService):
        """Create a new appointment."""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return make_response(jsonify({'error': 'No JSON data provided'}), 400)
            
            logger.info(f"Creating appointment for user {user_id}")
            
            appointment = service.create_appointment(
                trainer_id=user_id,
                appointment_data=data
            )
            
            return make_response(jsonify(appointment), 201)
            
        except Exception as e:
            logger.error(f"Error creating appointment: {str(e)}")
            return make_response(jsonify({'error': str(e)}), 500)


class AppointmentResource(Resource):
    """Resource for individual appointment operations."""
    
    @jwt_required()
    @inject('appointment_service')
    def get(self, appointment_id, service: IAppointmentService):
        """Get a specific appointment."""
        try:
            user_id = get_jwt_identity()
            logger.info(f"Fetching appointment {appointment_id} for user {user_id}")
            
            # For now, use get_appointments with filters
            result = service.get_appointments(user_id=user_id)
            appointments = result.get('appointments', [])
            
            appointment = next((a for a in appointments if a['id'] == appointment_id), None)
            
            if not appointment:
                return make_response(jsonify({'error': 'Appointment not found'}), 404)
            
            return make_response(jsonify(appointment), 200)
            
        except Exception as e:
            logger.error(f"Error fetching appointment: {str(e)}")
            return make_response(jsonify({'error': str(e)}), 500)
    
    @jwt_required()
    @inject('appointment_service')
    def put(self, appointment_id, service: IAppointmentService):
        """Update an appointment."""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return make_response(jsonify({'error': 'No JSON data provided'}), 400)
            
            logger.info(f"Updating appointment {appointment_id} for user {user_id}")
            
            appointment = service.update_appointment(
                appointment_id=appointment_id,
                user_id=user_id,
                update_data=data
            )
            
            return make_response(jsonify(appointment), 200)
            
        except Exception as e:
            logger.error(f"Error updating appointment: {str(e)}")
            return make_response(jsonify({'error': str(e)}), 500)
    
    @jwt_required()
    @inject('appointment_service')
    def delete(self, appointment_id, service: IAppointmentService):
        """Delete an appointment."""
        try:
            user_id = get_jwt_identity()
            
            logger.info(f"Deleting appointment {appointment_id} for user {user_id}")
            
            result = service.delete_appointment(
                appointment_id=appointment_id,
                user_id=user_id
            )
            
            return make_response(jsonify(result), 200)
            
        except Exception as e:
            logger.error(f"Error deleting appointment: {str(e)}")
            return make_response(jsonify({'error': str(e)}), 500)


class AppointmentSyncResource(Resource):
    """Resource for syncing appointments with calendar."""
    
    @jwt_required()
    @inject('appointment_service')
    def post(self, appointment_id, service: IAppointmentService):
        """Sync appointment to calendar."""
        try:
            user_id = get_jwt_identity()
            
            logger.info(f"Syncing appointment {appointment_id} to calendar for user {user_id}")
            
            result = service.sync_to_calendar(
                appointment_id=appointment_id,
                user_id=user_id
            )
            
            return make_response(jsonify(result), 200)
            
        except Exception as e:
            logger.error(f"Error syncing appointment: {str(e)}")
            return make_response(jsonify({'error': str(e)}), 500)
    
    @jwt_required()
    @inject('appointment_service')
    def delete(self, appointment_id, service: IAppointmentService):
        """Remove appointment from calendar."""
        try:
            user_id = get_jwt_identity()
            
            logger.info(f"Unsyncing appointment {appointment_id} from calendar for user {user_id}")
            
            result = service.unsync_from_calendar(
                appointment_id=appointment_id,
                user_id=user_id
            )
            
            return make_response(jsonify(result), 200)
            
        except Exception as e:
            logger.error(f"Error unsyncing appointment: {str(e)}")
            return make_response(jsonify({'error': str(e)}), 500)


def register_appointment_resources(api):
    """Register appointment resources with the API."""
    api.add_resource(AppointmentListResource, '/api/appointments')
    api.add_resource(AppointmentResource, '/api/appointments/<int:appointment_id>')
    api.add_resource(AppointmentSyncResource, '/api/appointments/<int:appointment_id>/sync')