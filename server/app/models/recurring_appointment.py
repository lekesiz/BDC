"""Recurring appointment models."""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON, Date
from sqlalchemy.orm import relationship
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from dateutil.relativedelta import relativedelta

from app.extensions import db


class RecurringPattern(db.Model):
    """Recurring pattern for appointments."""
    __tablename__ = 'recurring_patterns'
    
    id = Column(Integer, primary_key=True)
    
    # Recurrence type
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    
    # Interval (e.g., every 2 weeks)
    interval = Column(Integer, default=1)
    
    # For weekly recurrence - days of week (stored as JSON array)
    # e.g., [1, 3, 5] for Mon, Wed, Fri (0=Sun, 6=Sat)
    days_of_week = Column(JSON, nullable=True)
    
    # For monthly recurrence
    day_of_month = Column(Integer, nullable=True)  # 1-31
    week_of_month = Column(Integer, nullable=True)  # 1-5 (5=last)
    day_of_week_month = Column(Integer, nullable=True)  # 0-6 (for "2nd Tuesday" type patterns)
    
    # End conditions
    end_type = Column(String(20), default='never')  # never, after_occurrences, by_date
    occurrences = Column(Integer, nullable=True)  # Number of occurrences if end_type='after_occurrences'
    end_date = Column(Date, nullable=True)  # End date if end_type='by_date'
    
    # Exceptions (dates to skip, stored as JSON array of date strings)
    exceptions = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointment_series = relationship('AppointmentSeries', back_populates='pattern', uselist=False)
    
    def generate_occurrences(self, start_date, duration, max_occurrences=365):
        """Generate occurrence dates based on the pattern."""
        occurrences = []
        
        # Convert frequency to rrule frequency
        freq_map = {
            'daily': DAILY,
            'weekly': WEEKLY,
            'monthly': MONTHLY,
            'yearly': YEARLY
        }
        
        freq = freq_map.get(self.frequency, WEEKLY)
        
        # Build rrule parameters
        rrule_params = {
            'freq': freq,
            'interval': self.interval,
            'dtstart': start_date
        }
        
        # Add end condition
        if self.end_type == 'after_occurrences' and self.occurrences:
            rrule_params['count'] = self.occurrences
        elif self.end_type == 'by_date' and self.end_date:
            rrule_params['until'] = datetime.combine(self.end_date, datetime.min.time())
        else:
            # Default to max_occurrences to prevent infinite loops
            rrule_params['count'] = max_occurrences
        
        # Add weekly parameters
        if self.frequency == 'weekly' and self.days_of_week:
            rrule_params['byweekday'] = self.days_of_week
        
        # Add monthly parameters
        if self.frequency == 'monthly':
            if self.day_of_month:
                rrule_params['bymonthday'] = self.day_of_month
            elif self.week_of_month and self.day_of_week_month is not None:
                # For patterns like "2nd Tuesday"
                from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU
                weekdays = [MO, TU, WE, TH, FR, SA, SU]
                weekday = weekdays[self.day_of_week_month]
                if self.week_of_month == 5:  # Last week
                    rrule_params['byweekday'] = weekday(-1)
                else:
                    rrule_params['byweekday'] = weekday(self.week_of_month)
        
        # Generate occurrences
        rule = rrule(**rrule_params)
        
        # Filter out exceptions
        exception_dates = set()
        if self.exceptions:
            exception_dates = {datetime.strptime(d, '%Y-%m-%d').date() for d in self.exceptions}
        
        for occurrence in rule:
            if occurrence.date() not in exception_dates:
                end_time = occurrence + duration
                occurrences.append({
                    'start_time': occurrence,
                    'end_time': end_time
                })
        
        return occurrences
    
    def add_exception(self, date):
        """Add an exception date."""
        if not self.exceptions:
            self.exceptions = []
        
        date_str = date.strftime('%Y-%m-%d') if isinstance(date, (datetime, Date)) else date
        if date_str not in self.exceptions:
            self.exceptions.append(date_str)
            db.session.commit()
    
    def remove_exception(self, date):
        """Remove an exception date."""
        if not self.exceptions:
            return
        
        date_str = date.strftime('%Y-%m-%d') if isinstance(date, (datetime, Date)) else date
        if date_str in self.exceptions:
            self.exceptions.remove(date_str)
            db.session.commit()
    
    def to_dict(self):
        """Return a dict representation."""
        return {
            'id': self.id,
            'frequency': self.frequency,
            'interval': self.interval,
            'days_of_week': self.days_of_week,
            'day_of_month': self.day_of_month,
            'week_of_month': self.week_of_month,
            'day_of_week_month': self.day_of_week_month,
            'end_type': self.end_type,
            'occurrences': self.occurrences,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'exceptions': self.exceptions
        }


class AppointmentSeries(db.Model):
    """Series of recurring appointments."""
    __tablename__ = 'appointment_series'
    
    id = Column(Integer, primary_key=True)
    
    # Series information
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Participants
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id', ondelete='CASCADE'), nullable=False)
    trainer_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Default appointment details
    duration_minutes = Column(Integer, nullable=False, default=60)
    location = Column(String(255), nullable=True)
    
    # Recurrence pattern
    pattern_id = Column(Integer, ForeignKey('recurring_patterns.id', ondelete='CASCADE'), nullable=False)
    
    # Series start date (first occurrence)
    start_date = Column(DateTime, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pattern = relationship('RecurringPattern', back_populates='appointment_series')
    beneficiary = relationship('Beneficiary', backref='appointment_series')
    trainer = relationship('User', backref='trainer_appointment_series')
    appointments = relationship('Appointment', back_populates='series', cascade='all, delete-orphan')
    
    def generate_appointments(self, until_date=None):
        """Generate individual appointment instances."""
        if not self.pattern:
            return []
        
        # Calculate duration
        duration = timedelta(minutes=self.duration_minutes)
        
        # Generate occurrences
        if until_date:
            # Temporarily adjust pattern to generate only until specified date
            original_end_type = self.pattern.end_type
            original_end_date = self.pattern.end_date
            
            self.pattern.end_type = 'by_date'
            self.pattern.end_date = until_date
            
            occurrences = self.pattern.generate_occurrences(self.start_date, duration)
            
            # Restore original pattern
            self.pattern.end_type = original_end_type
            self.pattern.end_date = original_end_date
        else:
            occurrences = self.pattern.generate_occurrences(self.start_date, duration)
        
        # Create appointments for occurrences that don't exist yet
        from app.models import Appointment
        created_appointments = []
        
        for occurrence in occurrences:
            # Check if appointment already exists for this occurrence
            existing = Appointment.query.filter_by(
                series_id=self.id,
                start_time=occurrence['start_time']
            ).first()
            
            if not existing:
                appointment = Appointment(
                    beneficiary_id=self.beneficiary_id,
                    trainer_id=self.trainer_id,
                    title=self.title,
                    description=self.description,
                    start_time=occurrence['start_time'],
                    end_time=occurrence['end_time'],
                    location=self.location,
                    status='scheduled',
                    series_id=self.id
                )
                db.session.add(appointment)
                created_appointments.append(appointment)
        
        if created_appointments:
            db.session.commit()
        
        return created_appointments
    
    def update_future_appointments(self, updates, from_date=None):
        """Update all future appointments in the series."""
        from app.models import Appointment
        
        if not from_date:
            from_date = datetime.utcnow()
        
        future_appointments = Appointment.query.filter(
            Appointment.series_id == self.id,
            Appointment.start_time >= from_date,
            Appointment.status == 'scheduled'
        ).all()
        
        for appointment in future_appointments:
            for key, value in updates.items():
                if hasattr(appointment, key):
                    setattr(appointment, key, value)
        
        db.session.commit()
        return len(future_appointments)
    
    def cancel_series(self, from_date=None):
        """Cancel all future appointments in the series."""
        self.is_active = False
        count = self.update_future_appointments({'status': 'cancelled'}, from_date)
        db.session.commit()
        return count
    
    def to_dict(self):
        """Return a dict representation."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'beneficiary_id': self.beneficiary_id,
            'trainer_id': self.trainer_id,
            'duration_minutes': self.duration_minutes,
            'location': self.location,
            'pattern': self.pattern.to_dict() if self.pattern else None,
            'start_date': self.start_date.isoformat(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }