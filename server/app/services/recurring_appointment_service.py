"""Recurring appointment service module."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.extensions import db
from app.models import Appointment, AppointmentSeries, RecurringPattern, User, Beneficiary
from app.services.email_service import EmailService
from app.utils.datetime_utils import parse_date, format_datetime


class RecurringAppointmentService:
    """Service for managing recurring appointments."""
    
    @staticmethod
    def create_recurring_appointment(
        trainer_id: int,
        beneficiary_id: int,
        title: str,
        pattern_data: Dict[str, Any],
        start_date: datetime,
        duration_minutes: int = 60,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Tuple[Optional[AppointmentSeries], Optional[str]]:
        """Create a new recurring appointment series.
        
        Args:
            trainer_id: ID of the trainer
            beneficiary_id: ID of the beneficiary
            title: Title of the appointment
            pattern_data: Recurrence pattern configuration
            start_date: First occurrence date
            duration_minutes: Duration of each appointment
            description: Optional description
            location: Optional location
            
        Returns:
            Tuple of (AppointmentSeries, error_message)
        """
        try:
            # Validate trainer and beneficiary exist
            trainer = User.query.get(trainer_id)
            if not trainer or trainer.role not in ['trainer', 'tenant_admin', 'super_admin']:
                return None, "Invalid trainer ID"
            
            beneficiary = Beneficiary.query.get(beneficiary_id)
            if not beneficiary:
                return None, "Invalid beneficiary ID"
            
            # Create recurrence pattern
            pattern = RecurringPattern(
                frequency=pattern_data.get('frequency', 'weekly'),
                interval=pattern_data.get('interval', 1),
                days_of_week=pattern_data.get('days_of_week'),
                day_of_month=pattern_data.get('day_of_month'),
                week_of_month=pattern_data.get('week_of_month'),
                day_of_week_month=pattern_data.get('day_of_week_month'),
                end_type=pattern_data.get('end_type', 'never'),
                occurrences=pattern_data.get('occurrences'),
                end_date=parse_date(pattern_data.get('end_date')) if pattern_data.get('end_date') else None
            )
            db.session.add(pattern)
            db.session.flush()
            
            # Create appointment series
            series = AppointmentSeries(
                title=title,
                description=description,
                beneficiary_id=beneficiary_id,
                trainer_id=trainer_id,
                duration_minutes=duration_minutes,
                location=location,
                pattern_id=pattern.id,
                start_date=start_date,
                is_active=True
            )
            db.session.add(series)
            db.session.flush()
            
            # Generate initial appointments (next 3 months)
            until_date = datetime.utcnow() + timedelta(days=90)
            appointments = series.generate_appointments(until_date)
            
            db.session.commit()
            
            # Send notification email
            if beneficiary.user.email:
                EmailService.send_recurring_appointment_created(
                    beneficiary.user.email,
                    {
                        'beneficiary_name': f"{beneficiary.user.first_name} {beneficiary.user.last_name}",
                        'trainer_name': f"{trainer.first_name} {trainer.last_name}",
                        'title': title,
                        'frequency': pattern.frequency,
                        'start_date': format_datetime(start_date),
                        'appointment_count': len(appointments)
                    }
                )
            
            return series, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating recurring appointment: {str(e)}"
    
    @staticmethod
    def update_series(
        series_id: int,
        updates: Dict[str, Any],
        update_future_only: bool = True,
        from_date: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        """Update a recurring appointment series.
        
        Args:
            series_id: ID of the series to update
            updates: Dictionary of fields to update
            update_future_only: If True, only update future appointments
            from_date: Update appointments from this date onwards
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            series = AppointmentSeries.query.get(series_id)
            if not series:
                return False, "Series not found"
            
            # Update series fields
            for key, value in updates.items():
                if hasattr(series, key) and key not in ['id', 'created_at', 'pattern_id']:
                    setattr(series, key, value)
            
            # Update future appointments if requested
            if update_future_only:
                appointment_updates = {}
                if 'title' in updates:
                    appointment_updates['title'] = updates['title']
                if 'description' in updates:
                    appointment_updates['description'] = updates['description']
                if 'location' in updates:
                    appointment_updates['location'] = updates['location']
                if 'trainer_id' in updates:
                    appointment_updates['trainer_id'] = updates['trainer_id']
                
                if appointment_updates:
                    updated_count = series.update_future_appointments(
                        appointment_updates, 
                        from_date
                    )
            
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating series: {str(e)}"
    
    @staticmethod
    def update_pattern(
        series_id: int,
        pattern_updates: Dict[str, Any],
        regenerate: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """Update the recurrence pattern of a series.
        
        Args:
            series_id: ID of the series
            pattern_updates: New pattern configuration
            regenerate: If True, regenerate future appointments
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            series = AppointmentSeries.query.get(series_id)
            if not series or not series.pattern:
                return False, "Series or pattern not found"
            
            # Update pattern
            for key, value in pattern_updates.items():
                if hasattr(series.pattern, key):
                    setattr(series.pattern, key, value)
            
            if regenerate:
                # Cancel all future appointments
                now = datetime.utcnow()
                future_appointments = Appointment.query.filter(
                    and_(
                        Appointment.series_id == series_id,
                        Appointment.start_time > now,
                        Appointment.status == 'scheduled'
                    )
                ).all()
                
                for apt in future_appointments:
                    apt.status = 'cancelled'
                
                # Generate new appointments based on updated pattern
                until_date = now + timedelta(days=90)
                series.generate_appointments(until_date)
            
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating pattern: {str(e)}"
    
    @staticmethod
    def add_exception(series_id: int, exception_date: datetime) -> Tuple[bool, Optional[str]]:
        """Add an exception date to the series.
        
        Args:
            series_id: ID of the series
            exception_date: Date to skip
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            series = AppointmentSeries.query.get(series_id)
            if not series or not series.pattern:
                return False, "Series not found"
            
            # Add exception to pattern
            series.pattern.add_exception(exception_date)
            
            # Cancel appointment on that date if it exists
            appointment = Appointment.query.filter(
                and_(
                    Appointment.series_id == series_id,
                    db.func.date(Appointment.start_time) == exception_date.date()
                )
            ).first()
            
            if appointment and appointment.status == 'scheduled':
                appointment.status = 'cancelled'
                appointment.notes = "Cancelled due to series exception"
            
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error adding exception: {str(e)}"
    
    @staticmethod
    def remove_exception(series_id: int, exception_date: datetime) -> Tuple[bool, Optional[str]]:
        """Remove an exception date from the series.
        
        Args:
            series_id: ID of the series
            exception_date: Date to restore
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            series = AppointmentSeries.query.get(series_id)
            if not series or not series.pattern:
                return False, "Series not found"
            
            # Remove exception from pattern
            series.pattern.remove_exception(exception_date)
            
            # Regenerate appointment for that date if needed
            duration = timedelta(minutes=series.duration_minutes)
            occurrences = series.pattern.generate_occurrences(
                series.start_date, 
                duration,
                max_occurrences=100
            )
            
            # Find if this date should have an occurrence
            for occ in occurrences:
                if occ['start_time'].date() == exception_date.date():
                    # Check if appointment already exists
                    existing = Appointment.query.filter(
                        and_(
                            Appointment.series_id == series_id,
                            db.func.date(Appointment.start_time) == exception_date.date()
                        )
                    ).first()
                    
                    if not existing:
                        # Create new appointment
                        appointment = Appointment(
                            beneficiary_id=series.beneficiary_id,
                            trainer_id=series.trainer_id,
                            title=series.title,
                            description=series.description,
                            start_time=occ['start_time'],
                            end_time=occ['end_time'],
                            location=series.location,
                            status='scheduled',
                            series_id=series.id,
                            is_recurring=True
                        )
                        db.session.add(appointment)
                    elif existing.status == 'cancelled':
                        # Reactivate cancelled appointment
                        existing.status = 'scheduled'
                        existing.notes = None
                    
                    break
            
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error removing exception: {str(e)}"
    
    @staticmethod
    def update_single_occurrence(
        appointment_id: int,
        updates: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Update a single occurrence without affecting the series.
        
        Args:
            appointment_id: ID of the appointment to update
            updates: Fields to update
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            appointment = Appointment.query.get(appointment_id)
            if not appointment:
                return False, "Appointment not found"
            
            # Detach from series if making significant changes
            if any(key in updates for key in ['start_time', 'end_time', 'trainer_id']):
                appointment.series_id = None
                appointment.is_recurring = False
            
            # Update fields
            for key, value in updates.items():
                if hasattr(appointment, key) and key not in ['id', 'series_id', 'created_at']:
                    setattr(appointment, key, value)
            
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating appointment: {str(e)}"
    
    @staticmethod
    def cancel_series(
        series_id: int,
        from_date: Optional[datetime] = None,
        reason: Optional[str] = None
    ) -> Tuple[int, Optional[str]]:
        """Cancel all future appointments in a series.
        
        Args:
            series_id: ID of the series to cancel
            from_date: Cancel from this date onwards
            reason: Optional cancellation reason
            
        Returns:
            Tuple of (cancelled_count, error_message)
        """
        try:
            series = AppointmentSeries.query.get(series_id)
            if not series:
                return 0, "Series not found"
            
            # Cancel the series
            count = series.cancel_series(from_date)
            
            if reason:
                # Add cancellation reason to appointments
                appointments = Appointment.query.filter(
                    and_(
                        Appointment.series_id == series_id,
                        Appointment.status == 'cancelled'
                    )
                ).all()
                
                for apt in appointments:
                    apt.notes = f"Cancelled: {reason}" if not apt.notes else f"{apt.notes}\nCancelled: {reason}"
            
            db.session.commit()
            
            # Send notification
            if series.beneficiary.user.email:
                EmailService.send_recurring_appointment_cancelled(
                    series.beneficiary.user.email,
                    {
                        'beneficiary_name': f"{series.beneficiary.user.first_name} {series.beneficiary.user.last_name}",
                        'title': series.title,
                        'cancelled_count': count,
                        'reason': reason or "No reason provided"
                    }
                )
            
            return count, None
            
        except Exception as e:
            db.session.rollback()
            return 0, f"Error cancelling series: {str(e)}"
    
    @staticmethod
    def get_series_by_appointment(appointment_id: int) -> Optional[AppointmentSeries]:
        """Get the series for a given appointment.
        
        Args:
            appointment_id: ID of the appointment
            
        Returns:
            AppointmentSeries or None
        """
        appointment = Appointment.query.get(appointment_id)
        if appointment and appointment.series_id:
            return appointment.series
        return None
    
    @staticmethod
    def get_upcoming_occurrences(
        series_id: int,
        limit: int = 10,
        from_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get upcoming occurrences for a series.
        
        Args:
            series_id: ID of the series
            limit: Maximum number of occurrences to return
            from_date: Start date for search
            
        Returns:
            List of appointment dictionaries
        """
        if not from_date:
            from_date = datetime.utcnow()
        
        appointments = Appointment.query.filter(
            and_(
                Appointment.series_id == series_id,
                Appointment.start_time >= from_date,
                Appointment.status == 'scheduled'
            )
        ).order_by(Appointment.start_time).limit(limit).all()
        
        return [apt.to_dict() for apt in appointments]
    
    @staticmethod
    def generate_more_occurrences(
        series_id: int,
        months_ahead: int = 3
    ) -> Tuple[int, Optional[str]]:
        """Generate more occurrences for a series.
        
        Args:
            series_id: ID of the series
            months_ahead: How many months ahead to generate
            
        Returns:
            Tuple of (created_count, error_message)
        """
        try:
            series = AppointmentSeries.query.get(series_id)
            if not series:
                return 0, "Series not found"
            
            until_date = datetime.utcnow() + timedelta(days=30 * months_ahead)
            appointments = series.generate_appointments(until_date)
            
            db.session.commit()
            return len(appointments), None
            
        except Exception as e:
            db.session.rollback()
            return 0, f"Error generating occurrences: {str(e)}"
    
    @staticmethod
    def check_conflicts(
        trainer_id: int,
        start_date: datetime,
        pattern_data: Dict[str, Any],
        duration_minutes: int,
        exclude_series_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Check for scheduling conflicts with existing appointments.
        
        Args:
            trainer_id: ID of the trainer
            start_date: Start date of the series
            pattern_data: Recurrence pattern
            duration_minutes: Duration of each appointment
            exclude_series_id: Series ID to exclude from conflict check
            
        Returns:
            List of conflicting appointments
        """
        # Create temporary pattern to generate occurrences
        pattern = RecurringPattern(**pattern_data)
        duration = timedelta(minutes=duration_minutes)
        
        # Generate occurrences for next 3 months
        occurrences = pattern.generate_occurrences(
            start_date,
            duration,
            max_occurrences=50
        )
        
        conflicts = []
        
        for occ in occurrences:
            # Check for conflicts with each occurrence
            query = Appointment.query.filter(
                and_(
                    Appointment.trainer_id == trainer_id,
                    Appointment.status == 'scheduled',
                    or_(
                        and_(
                            Appointment.start_time <= occ['start_time'],
                            Appointment.end_time > occ['start_time']
                        ),
                        and_(
                            Appointment.start_time < occ['end_time'],
                            Appointment.end_time >= occ['end_time']
                        )
                    )
                )
            )
            
            if exclude_series_id:
                query = query.filter(
                    or_(
                        Appointment.series_id != exclude_series_id,
                        Appointment.series_id.is_(None)
                    )
                )
            
            conflicting = query.all()
            
            for apt in conflicting:
                conflicts.append({
                    'occurrence_date': occ['start_time'],
                    'conflicting_appointment': apt.to_dict()
                })
        
        return conflicts