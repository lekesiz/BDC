"""Refactored appointment service with improved architecture."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import current_app

from app.models.appointment import Appointment
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.integration import UserIntegration
from app.services.calendar_service import CalendarService
from app.services.email_service import send_notification_email
from app.exceptions import NotFoundException, ForbiddenException, ValidationException


class AppointmentServiceRefactored:
    """Refactored appointment service with improved testability and separation of concerns."""
    
    def __init__(self, db_session):
        """Initialize with database session for better testability."""
        self.db = db_session
    
    def get_appointments_for_user(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated appointments for a user with filters."""
        user = self._get_user_or_404(user_id)
        
        # Build query based on user role
        query = self._build_appointments_query(user, start_date, end_date, status)
        
        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Serialize appointments
        appointments = [
            self._serialize_appointment(appointment, user)
            for appointment in pagination.items
        ]
        
        return {
            'appointments': appointments,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }
    
    def create_appointment(self, trainer_id: int, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new appointment with validation."""
        trainer = self._get_user_or_404(trainer_id)
        self._validate_trainer_permissions(trainer)
        
        # Validate appointment data
        validated_data = self._validate_appointment_data(appointment_data)
        
        # Verify beneficiary access
        beneficiary = self._get_beneficiary_with_access_check(
            validated_data['beneficiary_id'],
            trainer
        )
        
        # Create appointment
        appointment = Appointment(
            title=validated_data['title'],
            description=validated_data.get('description'),
            location=validated_data.get('location'),
            start_time=validated_data['start_time'],
            end_time=validated_data['end_time'],
            trainer_id=trainer_id,
            beneficiary_id=beneficiary.id,
            status='scheduled'
        )
        
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        
        return self._serialize_appointment(appointment, trainer)
    
    def update_appointment(
        self,
        appointment_id: int,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing appointment."""
        user = self._get_user_or_404(user_id)
        appointment = self._get_appointment_with_access_check(appointment_id, user)
        
        # Update allowed fields
        self._update_appointment_fields(appointment, update_data)
        
        self.db.commit()
        self.db.refresh(appointment)
        
        return self._serialize_appointment(appointment, user)
    
    def delete_appointment(self, appointment_id: int, user_id: int) -> Dict[str, str]:
        """Delete an appointment with proper cleanup."""
        user = self._get_user_or_404(user_id)
        appointment = self._get_appointment_with_access_check(appointment_id, user)
        
        # Remove from calendar if synced
        if appointment.calendar_event_id:
            self._remove_from_calendar(appointment, user_id)
        
        self.db.delete(appointment)
        self.db.commit()
        
        return {'message': 'Appointment deleted successfully'}
    
    def sync_to_calendar(self, appointment_id: int, user_id: int) -> Dict[str, Any]:
        """Sync appointment to external calendar."""
        user = self._get_user_or_404(user_id)
        appointment = self._get_appointment_with_access_check(appointment_id, user)
        
        # Check calendar integration
        integration = self._get_calendar_integration(user_id)
        if not integration:
            raise ValidationException("Google Calendar not connected")
        
        # Sync to calendar
        event_id = self._sync_appointment_to_calendar(appointment, user_id)
        
        # Update appointment with event ID
        appointment.calendar_event_id = event_id
        self.db.commit()
        
        # Send notification
        self._send_appointment_notification(appointment)
        
        return {
            'message': 'Appointment synced to Google Calendar successfully',
            'calendar_event_id': event_id
        }
    
    def unsync_from_calendar(self, appointment_id: int, user_id: int) -> Dict[str, str]:
        """Remove appointment from external calendar."""
        user = self._get_user_or_404(user_id)
        appointment = self._get_appointment_with_access_check(appointment_id, user)
        
        if not appointment.calendar_event_id:
            return {'message': 'Appointment is not synced to Google Calendar'}
        
        # Remove from calendar
        self._remove_from_calendar(appointment, user_id)
        
        # Update appointment
        appointment.calendar_event_id = None
        self.db.commit()
        
        return {'message': 'Appointment unsynced from Google Calendar successfully'}
    
    # Private helper methods
    
    def _get_user_or_404(self, user_id: int) -> User:
        """Get user or raise NotFoundException."""
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        return user
    
    def _get_appointment_or_404(self, appointment_id: int) -> Appointment:
        """Get appointment or raise NotFoundException."""
        appointment = self.db.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment:
            raise NotFoundException(f"Appointment {appointment_id} not found")
        return appointment
    
    def _get_beneficiary_or_404(self, beneficiary_id: int) -> Beneficiary:
        """Get beneficiary or raise NotFoundException."""
        beneficiary = self.db.query(Beneficiary).filter_by(id=beneficiary_id).first()
        if not beneficiary:
            raise NotFoundException(f"Beneficiary {beneficiary_id} not found")
        return beneficiary
    
    def _validate_trainer_permissions(self, user: User) -> None:
        """Validate that user has trainer permissions."""
        if user.role not in ['trainer', 'admin', 'super_admin']:
            raise ForbiddenException("Only trainers and admins can manage appointments")
    
    def _validate_appointment_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and parse appointment data."""
        # Check required fields
        required_fields = ['title', 'start_time', 'end_time', 'beneficiary_id']
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Missing required field: {field}")
        
        # Parse dates
        try:
            start_time = datetime.fromisoformat(
                data['start_time'].replace('Z', '+00:00')
            )
            end_time = datetime.fromisoformat(
                data['end_time'].replace('Z', '+00:00')
            )
        except (ValueError, AttributeError):
            raise ValidationException("Invalid date format")
        
        # Validate dates
        if start_time >= end_time:
            raise ValidationException("Start time must be before end time")
        
        if start_time < datetime.utcnow():
            raise ValidationException("Cannot create appointments in the past")
        
        return {
            'title': data['title'],
            'description': data.get('description'),
            'location': data.get('location'),
            'start_time': start_time,
            'end_time': end_time,
            'beneficiary_id': data['beneficiary_id']
        }
    
    def _get_beneficiary_with_access_check(
        self,
        beneficiary_id: int,
        trainer: User
    ) -> Beneficiary:
        """Get beneficiary and verify trainer has access."""
        beneficiary = self._get_beneficiary_or_404(beneficiary_id)
        
        # Check access permissions
        if trainer.role == 'trainer' and beneficiary.trainer_id != trainer.id:
            raise ForbiddenException("You do not have access to this beneficiary")
        
        return beneficiary
    
    def _get_appointment_with_access_check(
        self,
        appointment_id: int,
        user: User
    ) -> Appointment:
        """Get appointment and verify user has access."""
        appointment = self._get_appointment_or_404(appointment_id)
        
        # Check permissions based on role
        if user.role == 'trainer' and appointment.trainer_id != user.id:
            raise ForbiddenException("You do not have permission to access this appointment")
        
        return appointment
    
    def _build_appointments_query(
        self,
        user: User,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        status: Optional[str]
    ):
        """Build appointments query based on user role and filters."""
        query = self.db.query(Appointment)
        
        # Filter by user role
        if user.role == 'student':
            # Students see their own appointments
            beneficiary = self.db.query(Beneficiary).filter_by(user_id=user.id).first()
            if beneficiary:
                query = query.filter_by(beneficiary_id=beneficiary.id)
            else:
                query = query.filter_by(id=-1)  # Return empty query
        elif user.role == 'trainer':
            # Trainers see their appointments
            query = query.filter_by(trainer_id=user.id)
        # Admins see all appointments (no additional filter)
        
        # Apply date filters
        if start_date:
            query = query.filter(Appointment.start_time >= start_date)
        if end_date:
            query = query.filter(Appointment.end_time <= end_date)
        
        # Apply status filter
        if status:
            query = query.filter_by(status=status)
        
        # Order by start time
        return query.order_by(Appointment.start_time.desc())
    
    def _serialize_appointment(self, appointment: Appointment, user: User) -> Dict[str, Any]:
        """Serialize appointment with appropriate fields based on user role."""
        data = {
            'id': appointment.id,
            'title': appointment.title,
            'description': appointment.description,
            'location': appointment.location,
            'start_time': appointment.start_time.isoformat(),
            'end_time': appointment.end_time.isoformat(),
            'status': appointment.status,
            'calendar_event_id': appointment.calendar_event_id,
            'created_at': appointment.created_at.isoformat(),
            'updated_at': appointment.updated_at.isoformat()
        }
        
        # Include beneficiary info for trainers/admins
        if user.role != 'student' and appointment.beneficiary:
            data['beneficiary'] = {
                'id': appointment.beneficiary.id,
                'first_name': appointment.beneficiary.user.first_name,
                'last_name': appointment.beneficiary.user.last_name,
                'email': appointment.beneficiary.user.email
            }
        
        # Include trainer info
        if appointment.trainer:
            data['trainer'] = {
                'id': appointment.trainer.id,
                'first_name': appointment.trainer.first_name,
                'last_name': appointment.trainer.last_name,
                'email': appointment.trainer.email
            }
        
        return data
    
    def _update_appointment_fields(
        self,
        appointment: Appointment,
        update_data: Dict[str, Any]
    ) -> None:
        """Update appointment fields with validation."""
        # Update simple fields
        for field in ['title', 'description', 'location']:
            if field in update_data:
                setattr(appointment, field, update_data[field])
        
        # Update status if valid
        if 'status' in update_data:
            valid_statuses = ['scheduled', 'completed', 'cancelled']
            if update_data['status'] in valid_statuses:
                appointment.status = update_data['status']
        
        # Update dates if provided
        if 'start_time' in update_data:
            try:
                appointment.start_time = datetime.fromisoformat(
                    update_data['start_time'].replace('Z', '+00:00')
                )
            except (ValueError, AttributeError):
                raise ValidationException("Invalid start time format")
        
        if 'end_time' in update_data:
            try:
                appointment.end_time = datetime.fromisoformat(
                    update_data['end_time'].replace('Z', '+00:00')
                )
            except (ValueError, AttributeError):
                raise ValidationException("Invalid end time format")
        
        # Validate dates after update
        if appointment.start_time >= appointment.end_time:
            raise ValidationException("Start time must be before end time")
    
    def _get_calendar_integration(self, user_id: int) -> Optional[UserIntegration]:
        """Get user's calendar integration if active."""
        return self.db.query(UserIntegration).filter_by(
            user_id=user_id,
            provider='google_calendar',
            status='active'
        ).first()
    
    def _sync_appointment_to_calendar(
        self,
        appointment: Appointment,
        user_id: int
    ) -> str:
        """Sync appointment to external calendar and return event ID."""
        appointment_data = {
            'title': f"Meeting with {appointment.beneficiary.user.first_name} {appointment.beneficiary.user.last_name}",
            'description': appointment.description or f"Scheduled appointment",
            'start_time': appointment.start_time,
            'end_time': appointment.end_time,
            'location': appointment.location,
            'attendees': [appointment.beneficiary.user.email]
        }
        
        if appointment.calendar_event_id:
            # Update existing event
            success = CalendarService.update_calendar_event(
                user_id=user_id,
                event_id=appointment.calendar_event_id,
                appointment=appointment_data
            )
            if not success:
                raise ValidationException("Failed to update calendar event")
            return appointment.calendar_event_id
        else:
            # Create new event
            event_id = CalendarService.create_calendar_event(
                user_id=user_id,
                appointment=appointment_data
            )
            if not event_id:
                raise ValidationException("Failed to create calendar event")
            return event_id
    
    def _remove_from_calendar(self, appointment: Appointment, user_id: int) -> None:
        """Remove appointment from external calendar."""
        integration = self._get_calendar_integration(user_id)
        if integration:
            try:
                CalendarService.delete_calendar_event(
                    user_id=user_id,
                    event_id=appointment.calendar_event_id
                )
            except Exception as e:
                current_app.logger.warning(
                    f"Failed to delete calendar event {appointment.calendar_event_id}: {str(e)}"
                )
    
    def _send_appointment_notification(self, appointment: Appointment) -> None:
        """Send notification email to beneficiary."""
        try:
            send_notification_email(
                user=appointment.beneficiary.user,
                notification={
                    'subject': f"Appointment with {appointment.trainer.first_name} {appointment.trainer.last_name}",
                    'message': f"You have a scheduled appointment on {appointment.start_time.strftime('%Y-%m-%d at %H:%M')}."
                }
            )
        except Exception as e:
            current_app.logger.error(
                f"Failed to send appointment notification: {str(e)}"
            )