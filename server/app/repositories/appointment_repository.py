"""Appointment repository implementation."""

from datetime import datetime
from app.models.appointment import Appointment
from app.services.interfaces.appointment_repository_interface import IAppointmentRepository


class AppointmentRepository(IAppointmentRepository):
    """Implementation of IAppointmentRepository."""
    
    def __init__(self, session):
        """Initialize with database session."""
        self.session = session
    
    def find_by_id(self, appointment_id):
        """Find appointment by ID."""
        return self.session.get(Appointment, appointment_id)
    
    def find_all(self, filters=None, pagination=None):
        """Find all appointments matching filters with pagination."""
        query = Appointment.query
        
        if filters:
            # Apply user/role filters
            if 'user_id' in filters:
                user_id = filters['user_id']
                role = filters.get('role', 'student')
                
                if role == 'student':
                    # Students see appointments where they are the beneficiary
                    query = query.join(Appointment.beneficiary).filter(
                        Appointment.beneficiary.has(user_id=user_id)
                    )
                elif role == 'trainer':
                    # Trainers see appointments where they are the trainer
                    query = query.filter(Appointment.trainer_id == user_id)
                # Admins and others see all appointments (no additional filter needed)
            
            # Apply date filters
            if 'start_date' in filters:
                query = query.filter(Appointment.start_time >= filters['start_date'])
            
            if 'end_date' in filters:
                query = query.filter(Appointment.end_time <= filters['end_date'])
            
            # Apply status filter
            if 'status' in filters:
                query = query.filter(Appointment.status == filters['status'])
        
        # Order by start time
        query = query.order_by(Appointment.start_time.desc())
        
        # Apply pagination
        if pagination:
            page = pagination.get('page', 1)
            per_page = pagination.get('per_page', 10)
            
            paginated = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'items': paginated.items,
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }
        
        return query.all()
    
    def create(self, appointment_data):
        """Create a new appointment."""
        appointment = Appointment(**appointment_data)
        self.session.add(appointment)
        self.session.commit()
        return appointment
    
    def update(self, appointment_id, update_data):
        """Update an existing appointment."""
        appointment = self.find_by_id(appointment_id)
        if appointment:
            for key, value in update_data.items():
                setattr(appointment, key, value)
            self.session.commit()
        return appointment
    
    def delete(self, appointment_id):
        """Delete an appointment."""
        appointment = self.find_by_id(appointment_id)
        if appointment:
            self.session.delete(appointment)
            self.session.commit()
            return True
        return False
    
    def find_by_beneficiary(self, beneficiary_id, pagination=None):
        """Find appointments for a beneficiary."""
        query = Appointment.query.filter_by(beneficiary_id=beneficiary_id)
        query = query.order_by(Appointment.start_time.desc())
        
        if pagination:
            page = pagination.get('page', 1)
            per_page = pagination.get('per_page', 10)
            
            paginated = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'items': paginated.items,
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }
        
        return query.all()
    
    def find_by_trainer(self, trainer_id, pagination=None):
        """Find appointments for a trainer."""
        query = Appointment.query.filter_by(trainer_id=trainer_id)
        query = query.order_by(Appointment.start_time.desc())
        
        if pagination:
            page = pagination.get('page', 1)
            per_page = pagination.get('per_page', 10)
            
            paginated = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'items': paginated.items,
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }
        
        return query.all()