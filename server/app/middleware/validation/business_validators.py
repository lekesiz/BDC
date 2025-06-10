"""
Business logic validators specific to the BDC project.
"""

import re
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from app.models import User, Program, Beneficiary, Appointment
from app.extensions import db


class BeneficiaryValidator:
    """Validator for beneficiary-related business rules."""
    
    @staticmethod
    def validate_registration(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate beneficiary registration data."""
        errors = {}
        
        # Validate age
        if 'date_of_birth' in data:
            dob = data['date_of_birth']
            if isinstance(dob, str):
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            
            age = (date.today() - dob).days // 365
            
            if age < 16:
                errors['date_of_birth'] = 'Beneficiary must be at least 16 years old'
            elif age > 100:
                errors['date_of_birth'] = 'Invalid date of birth'
        
        # Validate emergency contact
        if data.get('emergency_contact_phone') == data.get('phone'):
            errors['emergency_contact_phone'] = 'Emergency contact must be different from primary phone'
        
        # Validate unique identifier (if applicable)
        if 'national_id' in data:
            if not re.match(r'^\d{9,12}$', data['national_id']):
                errors['national_id'] = 'Invalid national ID format'
            
            # Check uniqueness
            existing = Beneficiary.query.filter_by(
                national_id=data['national_id']
            ).first()
            if existing:
                errors['national_id'] = 'National ID already registered'
        
        if errors:
            raise ValueError(errors)
        
        return data
    
    @staticmethod
    def validate_program_enrollment(beneficiary_id: int, program_id: int) -> bool:
        """Validate if beneficiary can enroll in program."""
        beneficiary = Beneficiary.query.get(beneficiary_id)
        program = Program.query.get(program_id)
        
        if not beneficiary or not program:
            raise ValueError("Invalid beneficiary or program")
        
        # Check if already enrolled
        if beneficiary in program.enrolled_beneficiaries:
            raise ValueError("Beneficiary is already enrolled in this program")
        
        # Check program capacity
        if program.max_participants and len(program.enrolled_beneficiaries) >= program.max_participants:
            raise ValueError("Program is at full capacity")
        
        # Check prerequisites
        if program.prerequisites:
            completed_programs = [p.id for p in beneficiary.completed_programs]
            for prereq_id in program.prerequisites:
                if prereq_id not in completed_programs:
                    raise ValueError("Beneficiary has not completed required prerequisites")
        
        # Check eligibility criteria (age, location, etc.)
        if program.min_age and beneficiary.age < program.min_age:
            raise ValueError(f"Beneficiary must be at least {program.min_age} years old")
        
        if program.max_age and beneficiary.age > program.max_age:
            raise ValueError(f"Beneficiary must be no more than {program.max_age} years old")
        
        return True


class AppointmentValidator:
    """Validator for appointment-related business rules."""
    
    @staticmethod
    def validate_booking(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate appointment booking."""
        errors = {}
        
        # Validate appointment time
        appointment_datetime = data.get('appointment_datetime')
        if isinstance(appointment_datetime, str):
            appointment_datetime = datetime.fromisoformat(appointment_datetime)
        
        # Check if in the future
        if appointment_datetime <= datetime.now():
            errors['appointment_datetime'] = 'Appointment must be in the future'
        
        # Check business hours (assuming 8 AM - 6 PM)
        if appointment_datetime.hour < 8 or appointment_datetime.hour >= 18:
            errors['appointment_datetime'] = 'Appointment must be during business hours (8 AM - 6 PM)'
        
        # Check weekdays only
        if appointment_datetime.weekday() >= 5:  # Saturday = 5, Sunday = 6
            errors['appointment_datetime'] = 'Appointments are only available on weekdays'
        
        # Check minimum advance booking (e.g., 24 hours)
        min_advance = datetime.now() + timedelta(hours=24)
        if appointment_datetime < min_advance:
            errors['appointment_datetime'] = 'Appointments must be booked at least 24 hours in advance'
        
        # Check maximum advance booking (e.g., 90 days)
        max_advance = datetime.now() + timedelta(days=90)
        if appointment_datetime > max_advance:
            errors['appointment_datetime'] = 'Appointments cannot be booked more than 90 days in advance'
        
        # Validate duration
        duration = data.get('duration_minutes', 60)
        if duration < 15:
            errors['duration_minutes'] = 'Appointment duration must be at least 15 minutes'
        elif duration > 240:
            errors['duration_minutes'] = 'Appointment duration cannot exceed 4 hours'
        elif duration % 15 != 0:
            errors['duration_minutes'] = 'Appointment duration must be in 15-minute increments'
        
        # Check for conflicts
        if 'trainer_id' in data and 'beneficiary_id' in data:
            conflicts = AppointmentValidator._check_conflicts(
                data['trainer_id'],
                data['beneficiary_id'],
                appointment_datetime,
                duration
            )
            if conflicts:
                errors['appointment_datetime'] = conflicts
        
        if errors:
            raise ValueError(errors)
        
        return data
    
    @staticmethod
    def _check_conflicts(trainer_id: int, beneficiary_id: int, 
                        start_time: datetime, duration: int) -> Optional[str]:
        """Check for scheduling conflicts."""
        end_time = start_time + timedelta(minutes=duration)
        
        # Check trainer conflicts
        trainer_conflicts = Appointment.query.filter(
            Appointment.trainer_id == trainer_id,
            Appointment.status.in_(['scheduled', 'confirmed']),
            db.or_(
                db.and_(
                    Appointment.appointment_datetime >= start_time,
                    Appointment.appointment_datetime < end_time
                ),
                db.and_(
                    Appointment.appointment_datetime <= start_time,
                    Appointment.appointment_datetime + timedelta(minutes=Appointment.duration_minutes) > start_time
                )
            )
        ).first()
        
        if trainer_conflicts:
            return "Trainer has another appointment at this time"
        
        # Check beneficiary conflicts
        beneficiary_conflicts = Appointment.query.filter(
            Appointment.beneficiary_id == beneficiary_id,
            Appointment.status.in_(['scheduled', 'confirmed']),
            db.or_(
                db.and_(
                    Appointment.appointment_datetime >= start_time,
                    Appointment.appointment_datetime < end_time
                ),
                db.and_(
                    Appointment.appointment_datetime <= start_time,
                    Appointment.appointment_datetime + timedelta(minutes=Appointment.duration_minutes) > start_time
                )
            )
        ).first()
        
        if beneficiary_conflicts:
            return "Beneficiary has another appointment at this time"
        
        return None
    
    @staticmethod
    def validate_cancellation(appointment_id: int, user_id: int) -> bool:
        """Validate appointment cancellation."""
        appointment = Appointment.query.get(appointment_id)
        
        if not appointment:
            raise ValueError("Appointment not found")
        
        # Check if appointment can be cancelled
        if appointment.status in ['completed', 'cancelled']:
            raise ValueError(f"Cannot cancel {appointment.status} appointment")
        
        # Check cancellation policy (e.g., 4 hours notice)
        min_notice = appointment.appointment_datetime - timedelta(hours=4)
        if datetime.now() > min_notice:
            raise ValueError("Appointments must be cancelled at least 4 hours in advance")
        
        # Check authorization
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Invalid user")
        
        # User can cancel if they're the trainer, beneficiary, or admin
        if user.role == 'admin':
            return True
        elif user.role == 'trainer' and appointment.trainer_id == user.id:
            return True
        elif user.role == 'beneficiary' and appointment.beneficiary_id == user.id:
            return True
        else:
            raise ValueError("You are not authorized to cancel this appointment")


class ProgramValidator:
    """Validator for program-related business rules."""
    
    @staticmethod
    def validate_program_creation(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate program creation data."""
        errors = {}
        
        # Validate dates
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date < date.today():
            errors['start_date'] = 'Program start date cannot be in the past'
        
        if end_date <= start_date:
            errors['end_date'] = 'Program end date must be after start date'
        
        # Validate duration
        duration_days = (end_date - start_date).days
        if duration_days < 7:
            errors['duration'] = 'Program must be at least 7 days long'
        elif duration_days > 365:
            errors['duration'] = 'Program cannot exceed 1 year'
        
        # Validate capacity
        max_participants = data.get('max_participants')
        if max_participants is not None:
            if max_participants < 1:
                errors['max_participants'] = 'Maximum participants must be at least 1'
            elif max_participants > 1000:
                errors['max_participants'] = 'Maximum participants cannot exceed 1000'
        
        # Validate sessions
        sessions_per_week = data.get('sessions_per_week', 1)
        if sessions_per_week < 1:
            errors['sessions_per_week'] = 'Must have at least 1 session per week'
        elif sessions_per_week > 7:
            errors['sessions_per_week'] = 'Cannot have more than 7 sessions per week'
        
        # Validate unique name within tenant
        if 'name' in data and 'tenant_id' in data:
            existing = Program.query.filter_by(
                name=data['name'],
                tenant_id=data['tenant_id']
            ).first()
            if existing:
                errors['name'] = 'A program with this name already exists'
        
        if errors:
            raise ValueError(errors)
        
        return data
    
    @staticmethod
    def validate_session_attendance(session_id: int, beneficiary_id: int) -> bool:
        """Validate session attendance marking."""
        from app.models import ProgramSession
        
        session = ProgramSession.query.get(session_id)
        if not session:
            raise ValueError("Session not found")
        
        # Check if session has started
        if session.scheduled_datetime > datetime.now():
            raise ValueError("Cannot mark attendance for future sessions")
        
        # Check if beneficiary is enrolled in program
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if beneficiary not in session.program.enrolled_beneficiaries:
            raise ValueError("Beneficiary is not enrolled in this program")
        
        # Check if attendance already marked
        existing_attendance = session.attendances.filter_by(
            beneficiary_id=beneficiary_id
        ).first()
        if existing_attendance:
            raise ValueError("Attendance already marked for this session")
        
        return True


class EvaluationValidator:
    """Validator for evaluation-related business rules."""
    
    @staticmethod
    def validate_evaluation_submission(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate evaluation submission."""
        errors = {}
        
        # Validate scores
        if 'scores' in data:
            for category, score in data['scores'].items():
                if not isinstance(score, (int, float)):
                    errors[f'scores.{category}'] = 'Score must be a number'
                elif score < 0 or score > 100:
                    errors[f'scores.{category}'] = 'Score must be between 0 and 100'
        
        # Validate completion time
        if 'time_taken_minutes' in data:
            time_taken = data['time_taken_minutes']
            if time_taken < 1:
                errors['time_taken_minutes'] = 'Time taken must be at least 1 minute'
            elif time_taken > 480:  # 8 hours
                errors['time_taken_minutes'] = 'Time taken seems unrealistic (max 8 hours)'
        
        # Validate submission deadline
        if 'evaluation_id' in data:
            from app.models import Evaluation
            evaluation = Evaluation.query.get(data['evaluation_id'])
            
            if evaluation and evaluation.deadline:
                if datetime.now() > evaluation.deadline:
                    errors['submission'] = 'Evaluation deadline has passed'
        
        # Validate file attachments
        if 'attachments' in data:
            total_size = 0
            for attachment in data['attachments']:
                if 'size' in attachment:
                    total_size += attachment['size']
            
            if total_size > 50 * 1024 * 1024:  # 50MB
                errors['attachments'] = 'Total attachment size cannot exceed 50MB'
        
        if errors:
            raise ValueError(errors)
        
        return data


class UserValidator:
    """Validator for user-related business rules."""
    
    @staticmethod
    def validate_role_change(user_id: int, new_role: str, admin_id: int) -> bool:
        """Validate user role change."""
        user = User.query.get(user_id)
        admin = User.query.get(admin_id)
        
        if not user or not admin:
            raise ValueError("Invalid user or admin")
        
        # Check admin permissions
        if admin.role != 'admin' and admin.role != 'super_admin':
            raise ValueError("Only admins can change user roles")
        
        # Validate new role
        valid_roles = ['student', 'trainer', 'admin', 'tenant_admin']
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        # Prevent demoting super admin
        if user.role == 'super_admin':
            raise ValueError("Cannot change super admin role")
        
        # Check tenant boundaries
        if user.tenant_id != admin.tenant_id and admin.role != 'super_admin':
            raise ValueError("Cannot change roles for users in different tenants")
        
        # Special checks for admin role
        if new_role == 'admin':
            # Limit number of admins per tenant
            admin_count = User.query.filter_by(
                tenant_id=user.tenant_id,
                role='admin',
                is_active=True
            ).count()
            
            if admin_count >= 5:
                raise ValueError("Maximum number of admins reached for this tenant")
        
        return True
    
    @staticmethod
    def validate_profile_update(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user profile update."""
        errors = {}
        
        # Validate username change
        if 'username' in data:
            username = data['username']
            
            # Check format
            if not re.match(r'^[a-zA-Z0-9_\-\.]{3,30}$', username):
                errors['username'] = 'Username must be 3-30 characters and contain only letters, numbers, underscore, hyphen, or dot'
            
            # Check uniqueness
            existing = User.query.filter_by(username=username).first()
            if existing and existing.id != user_id:
                errors['username'] = 'Username already taken'
        
        # Validate timezone
        if 'timezone' in data:
            import pytz
            try:
                pytz.timezone(data['timezone'])
            except pytz.exceptions.UnknownTimeZoneError:
                errors['timezone'] = 'Invalid timezone'
        
        # Validate language
        if 'language' in data:
            supported_languages = ['en', 'es', 'fr', 'ar', 'de', 'ru', 'tr']
            if data['language'] not in supported_languages:
                errors['language'] = f"Language must be one of: {', '.join(supported_languages)}"
        
        if errors:
            raise ValueError(errors)
        
        return data