"""Appointment service implementation module."""

from datetime import datetime, timedelta
from flask import current_app

from app.services.interfaces.appointment_service_interface import IAppointmentService
from app.services.interfaces.appointment_repository_interface import IAppointmentRepository
from app.services.interfaces.user_repository_interface import IUserRepository
from app.services.interfaces.beneficiary_repository_interface import IBeneficiaryRepository
from app.models.integration import UserIntegration
from app.models.user import User
from app.services.calendar_service import CalendarService
from app.services.email_service import send_notification_email
from app.exceptions import NotFoundException, ForbiddenException, ValidationException


class AppointmentService(IAppointmentService):
    """Implementation of IAppointmentService."""
    
    def __init__(self, appointment_repository, user_repository, beneficiary_repository):
        """
        Initialize the appointment service.
        
        Args:
            appointment_repository: Instance of IAppointmentRepository
            user_repository: Instance of IUserRepository
            beneficiary_repository: Instance of IBeneficiaryRepository
        """
        self.appointment_repository = appointment_repository
        self.user_repository = user_repository
        self.beneficiary_repository = beneficiary_repository
    
    def get_appointments(self, user_id, page=1, per_page=10, start_date=None, end_date=None, status=None):
        """
        Get paginated appointments for a user.
        
        Args:
            user_id: The user's ID
            page: Page number
            per_page: Items per page
            start_date: Filter appointments from this date
            end_date: Filter appointments to this date
            status: Filter by appointment status
            
        Returns:
            Dict containing appointments, total count, pages, and current page
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        
        # Parse dates if provided as strings
        filters = {
            'user_id': user_id,
            'role': user.role,
        }
        
        if start_date:
            try:
                if isinstance(start_date, str):
                    filters['start_date'] = datetime.strptime(start_date, '%Y-%m-%d')
                else:
                    filters['start_date'] = start_date
            except ValueError:
                pass
        
        if end_date:
            try:
                if isinstance(end_date, str):
                    filters['end_date'] = datetime.strptime(end_date, '%Y-%m-%d')
                else:
                    filters['end_date'] = end_date
            except ValueError:
                pass
        
        if status:
            filters['status'] = status
        
        # Get appointments
        result = self.appointment_repository.find_all(
            filters=filters,
            pagination={'page': page, 'per_page': per_page}
        )
        
        # Serialize appointments
        appointments = []
        for appointment in result['items']:
            appointment_dict = appointment.to_dict()
            
            # Include beneficiary info for trainers/admins
            if user.role != 'student' and appointment.beneficiary:
                appointment_dict['beneficiary'] = {
                    'id': appointment.beneficiary.id,
                    'first_name': appointment.beneficiary.user.first_name,
                    'last_name': appointment.beneficiary.user.last_name,
                    'email': appointment.beneficiary.user.email
                }
            
            # Include trainer info
            if appointment.trainer:
                appointment_dict['trainer'] = {
                    'id': appointment.trainer.id,
                    'first_name': appointment.trainer.first_name,
                    'last_name': appointment.trainer.last_name,
                    'email': appointment.trainer.email
                }
            
            appointments.append(appointment_dict)
        
        return {
            'appointments': appointments,
            'total': result['total'],
            'pages': result['pages'],
            'current_page': result['current_page']
        }
    
    def create_appointment(self, trainer_id, appointment_data):
        """
        Create a new appointment.
        
        Args:
            trainer_id: The trainer's user ID
            appointment_data: Dict containing appointment details
            
        Returns:
            Created appointment object
        """
        user = self.user_repository.find_by_id(trainer_id)
        if not user:
            raise NotFoundException(f"User {trainer_id} not found")
        
        # Validate user role
        if user.role not in ['trainer', 'admin', 'super_admin']:
            raise ForbiddenException("Only trainers and admins can create appointments")
        
        # Validate required fields
        required_fields = ['title', 'start_time', 'end_time', 'beneficiary_id']
        for field in required_fields:
            if field not in appointment_data:
                raise ValidationException(f"Missing required field: {field}")
        
        # Parse dates
        try:
            start_time = datetime.fromisoformat(appointment_data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(appointment_data['end_time'].replace('Z', '+00:00'))
        except ValueError:
            raise ValidationException("Invalid date format")
        
        # Validate dates
        if start_time >= end_time:
            raise ValidationException("Start time must be before end time")
        
        if start_time < datetime.utcnow():
            raise ValidationException("Cannot create appointments in the past")
        
        # Verify beneficiary exists and trainer has access
        beneficiary = self.beneficiary_repository.find_by_id(appointment_data['beneficiary_id'])
        if not beneficiary:
            raise NotFoundException("Beneficiary not found")
        
        # Check permissions
        if user.role == 'trainer' and beneficiary.trainer_id != trainer_id:
            raise ForbiddenException("You do not have access to this beneficiary")
        
        # Create appointment
        appointment_data.update({
            'start_time': start_time,
            'end_time': end_time,
            'trainer_id': trainer_id,
            'status': 'scheduled'
        })
        
        appointment = self.appointment_repository.create(appointment_data)
        return appointment.to_dict()
    
    def update_appointment(self, appointment_id, user_id, update_data):
        """
        Update an existing appointment.
        
        Args:
            appointment_id: The appointment ID
            user_id: The requesting user's ID
            update_data: Dict containing updated appointment data
            
        Returns:
            Updated appointment object
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise NotFoundException(f"Appointment {appointment_id} not found")
        
        # Check permissions
        if user.role == 'trainer' and appointment.trainer_id != user_id:
            raise ForbiddenException("You do not have permission to update this appointment")
        
        # Prepare update data
        clean_update_data = {}
        
        # Update simple fields
        for field in ['title', 'description', 'location']:
            if field in update_data:
                clean_update_data[field] = update_data[field]
        
        # Update status if valid
        if 'status' in update_data and update_data['status'] in ['scheduled', 'completed', 'cancelled']:
            clean_update_data['status'] = update_data['status']
        
        # Update dates if provided
        if 'start_time' in update_data:
            try:
                start_time = datetime.fromisoformat(update_data['start_time'].replace('Z', '+00:00'))
                clean_update_data['start_time'] = start_time
            except ValueError:
                raise ValidationException("Invalid start time format")
        
        if 'end_time' in update_data:
            try:
                end_time = datetime.fromisoformat(update_data['end_time'].replace('Z', '+00:00'))
                clean_update_data['end_time'] = end_time
            except ValueError:
                raise ValidationException("Invalid end time format")
        
        # Update the appointment
        updated_appointment = self.appointment_repository.update(appointment_id, clean_update_data)
        if not updated_appointment:
            raise NotFoundException("Failed to update appointment")
        
        # Validate dates after update
        if updated_appointment.start_time >= updated_appointment.end_time:
            raise ValidationException("Start time must be before end time")
        
        return updated_appointment.to_dict()
    
    def delete_appointment(self, appointment_id, user_id):
        """
        Delete an appointment.
        
        Args:
            appointment_id: The appointment ID
            user_id: The requesting user's ID
            
        Returns:
            Success message
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise NotFoundException(f"Appointment {appointment_id} not found")
        
        # Check permissions
        if user.role not in ['admin', 'super_admin']:
            if user.role == 'trainer' and appointment.trainer_id != user_id:
                raise ForbiddenException("You do not have permission to delete this appointment")
        
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
        
        self.appointment_repository.delete(appointment_id)
        return {'message': 'Appointment deleted successfully'}
    
    def sync_to_calendar(self, appointment_id, user_id):
        """
        Sync appointment to Google Calendar.
        
        Args:
            appointment_id: The appointment ID
            user_id: The requesting user's ID
            
        Returns:
            Dict containing sync status and event ID
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        
        # Check if the user has an active integration
        integration = UserIntegration.query.filter_by(
            user_id=user_id,
            provider='google_calendar',
            status='active'
        ).first()
        
        if not integration:
            raise ValidationException("Google Calendar not connected")
        
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise NotFoundException(f"Appointment {appointment_id} not found")
        
        # Check permissions
        if appointment.trainer_id != user_id and user.role not in ['super_admin', 'tenant_admin']:
            raise ForbiddenException("Not authorized to sync this appointment")
        
        # Prepare appointment data for calendar
        appointment_data = {
            'title': f"Meeting with {appointment.beneficiary.user.first_name} {appointment.beneficiary.user.last_name}",
            'description': appointment.description or f"Scheduled appointment with {appointment.beneficiary.user.first_name} {appointment.beneficiary.user.last_name}",
            'start_time': appointment.start_time,
            'end_time': appointment.end_time,
            'location': appointment.location,
            'attendees': [appointment.beneficiary.user.email]
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
                raise ValidationException("Failed to update calendar event")
        else:
            # Create new event
            event_id = CalendarService.create_calendar_event(
                user_id=user_id,
                appointment=appointment_data
            )
            
            if not event_id:
                raise ValidationException("Failed to create calendar event")
            
            # Update appointment with event ID
            self.appointment_repository.update(appointment_id, {'calendar_event_id': event_id})
            appointment.calendar_event_id = event_id
        
        # Notify the beneficiary
        send_notification_email(
            user=appointment.beneficiary.user,
            notification={
                'subject': f"Appointment with {appointment.trainer.first_name} {appointment.trainer.last_name}",
                'message': f"You have a scheduled appointment with {appointment.trainer.first_name} {appointment.trainer.last_name} on {appointment.start_time.strftime('%Y-%m-%d at %H:%M')}."
            }
        )
        
        return {
            'message': 'Appointment synced to Google Calendar successfully',
            'calendar_event_id': appointment.calendar_event_id
        }
    
    def unsync_from_calendar(self, appointment_id, user_id):
        """
        Remove appointment from Google Calendar.
        
        Args:
            appointment_id: The appointment ID
            user_id: The requesting user's ID
            
        Returns:
            Success message
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise NotFoundException(f"Appointment {appointment_id} not found")
        
        # Check permissions
        if appointment.trainer_id != user_id and user.role not in ['super_admin', 'tenant_admin']:
            raise ForbiddenException("Not authorized to unsync this appointment")
        
        # Check if the appointment has a calendar event
        if not appointment.calendar_event_id:
            return {'message': 'Appointment is not synced to Google Calendar'}
        
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
        self.appointment_repository.update(appointment_id, {'calendar_event_id': None})
        
        return {'message': 'Appointment unsynced from Google Calendar successfully'}