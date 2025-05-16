"""Availability service module."""

from datetime import datetime, timedelta, time
import calendar
from flask import current_app

from app.extensions import db
from app.models.availability import AvailabilitySchedule, AvailabilitySlot, AvailabilityException
from app.models.appointment import Appointment


class AvailabilityService:
    """Availability service for managing trainer availability."""
    
    @staticmethod
    def get_or_create_default_schedule(user_id):
        """
        Get or create the default availability schedule for a user.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            AvailabilitySchedule: The availability schedule
        """
        # Check if user already has a default schedule
        schedule = AvailabilitySchedule.query.filter_by(
            user_id=user_id,
            title='Default Schedule'
        ).first()
        
        if schedule:
            return schedule
        
        # Create a new default schedule
        schedule = AvailabilitySchedule(
            user_id=user_id,
            title='Default Schedule',
            is_active=True,
            time_zone='UTC'
        )
        
        db.session.add(schedule)
        
        # Create default availability slots (Mon-Fri, 9 AM - 5 PM)
        for day in range(5):  # 0 = Monday, 4 = Friday
            slot = AvailabilitySlot(
                schedule=schedule,
                day_of_week=day,
                start_time='09:00',
                end_time='17:00',
                is_available=True
            )
            db.session.add(slot)
        
        db.session.commit()
        
        return schedule
    
    @staticmethod
    def get_user_availability(user_id, start_date, end_date):
        """
        Get a user's availability between two dates.
        
        Args:
            user_id (int): The user ID
            start_date (datetime): The start date
            end_date (datetime): The end date
            
        Returns:
            dict: The user's availability
        """
        # Get active schedule
        schedule = AvailabilitySchedule.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        
        if not schedule:
            schedule = AvailabilityService.get_or_create_default_schedule(user_id)
        
        # Get availability slots
        slots = AvailabilitySlot.query.filter_by(
            schedule_id=schedule.id
        ).all()
        
        # Get exceptions for the date range
        exceptions = AvailabilityException.query.filter(
            AvailabilityException.user_id == user_id,
            AvailabilityException.date >= start_date,
            AvailabilityException.date <= end_date
        ).all()
        
        # Get appointments for the date range
        appointments = Appointment.query.filter(
            Appointment.trainer_id == user_id,
            Appointment.start_time >= start_date,
            Appointment.end_time <= end_date,
            Appointment.status != 'cancelled'
        ).all()
        
        # Generate daily availability
        date_range = (end_date - start_date).days + 1
        availability = []
        
        for day in range(date_range):
            current_date = start_date + timedelta(days=day)
            day_of_week = current_date.weekday()  # 0 = Monday, 6 = Sunday
            
            # Get slots for current day
            day_slots = [slot for slot in slots if slot.day_of_week == day_of_week]
            
            # Get exceptions for current day
            day_exceptions = [e for e in exceptions if e.date.date() == current_date.date()]
            
            # Get appointments for current day
            day_appointments = [a for a in appointments if a.start_time.date() == current_date.date()]
            
            # Format times consistently
            day_availability = {
                'date': current_date.strftime('%Y-%m-%d'),
                'day_of_week': day_of_week,
                'day_name': calendar.day_name[day_of_week],
                'available_slots': [],
                'unavailable_slots': [],
                'appointments': []
            }
            
            # First, add regular slots
            for slot in day_slots:
                if slot.is_available:
                    day_availability['available_slots'].append({
                        'start_time': slot.start_time,
                        'end_time': slot.end_time,
                        'type': 'regular'
                    })
                else:
                    day_availability['unavailable_slots'].append({
                        'start_time': slot.start_time,
                        'end_time': slot.end_time,
                        'type': 'regular'
                    })
            
            # Then, apply exceptions
            for exception in day_exceptions:
                if exception.start_time and exception.end_time:
                    # Time-specific exception
                    if exception.is_available:
                        day_availability['available_slots'].append({
                            'start_time': exception.start_time,
                            'end_time': exception.end_time,
                            'type': 'exception',
                            'title': exception.title,
                            'description': exception.description
                        })
                    else:
                        day_availability['unavailable_slots'].append({
                            'start_time': exception.start_time,
                            'end_time': exception.end_time,
                            'type': 'exception',
                            'title': exception.title,
                            'description': exception.description
                        })
                else:
                    # All-day exception
                    if exception.is_available:
                        # Clear unavailable slots and add a full day available slot
                        day_availability['unavailable_slots'] = []
                        day_availability['available_slots'] = [{
                            'start_time': '00:00',
                            'end_time': '23:59',
                            'type': 'exception',
                            'title': exception.title,
                            'description': exception.description
                        }]
                    else:
                        # Clear available slots and add a full day unavailable slot
                        day_availability['available_slots'] = []
                        day_availability['unavailable_slots'] = [{
                            'start_time': '00:00',
                            'end_time': '23:59',
                            'type': 'exception',
                            'title': exception.title,
                            'description': exception.description
                        }]
            
            # Finally, add appointments
            for appointment in day_appointments:
                day_availability['appointments'].append({
                    'id': appointment.id,
                    'start_time': appointment.start_time.strftime('%H:%M'),
                    'end_time': appointment.end_time.strftime('%H:%M'),
                    'title': appointment.title,
                    'status': appointment.status
                })
            
            availability.append(day_availability)
        
        return {
            'user_id': user_id,
            'schedule_id': schedule.id,
            'schedule_title': schedule.title,
            'time_zone': schedule.time_zone,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'days': availability
        }
    
    @staticmethod
    def update_availability_schedule(schedule_id, data):
        """
        Update an availability schedule.
        
        Args:
            schedule_id (int): The schedule ID
            data (dict): The schedule data
            
        Returns:
            AvailabilitySchedule: The updated schedule or None if update fails
        """
        try:
            # Get the schedule
            schedule = AvailabilitySchedule.query.get(schedule_id)
            
            if not schedule:
                return None
            
            # Update schedule attributes
            if 'title' in data:
                schedule.title = data['title']
            
            if 'is_active' in data:
                schedule.is_active = data['is_active']
            
            if 'time_zone' in data:
                schedule.time_zone = data['time_zone']
            
            # Update slots if provided
            if 'slots' in data:
                # Delete existing slots
                AvailabilitySlot.query.filter_by(schedule_id=schedule_id).delete()
                
                # Create new slots
                for slot_data in data['slots']:
                    slot = AvailabilitySlot(
                        schedule_id=schedule_id,
                        day_of_week=slot_data['day_of_week'],
                        start_time=slot_data['start_time'],
                        end_time=slot_data['end_time'],
                        is_available=slot_data.get('is_available', True)
                    )
                    db.session.add(slot)
            
            db.session.commit()
            
            return schedule
            
        except Exception as e:
            current_app.logger.error(f"Error updating availability schedule: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def add_availability_exception(user_id, data):
        """
        Add an availability exception.
        
        Args:
            user_id (int): The user ID
            data (dict): The exception data
            
        Returns:
            AvailabilityException: The created exception or None if creation fails
        """
        try:
            # Parse date
            date_str = data.get('date')
            if not date_str:
                current_app.logger.error("Date is required for availability exception")
                return None
            
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                current_app.logger.error(f"Invalid date format: {date_str}")
                return None
            
            # Create exception
            exception = AvailabilityException(
                user_id=user_id,
                date=date,
                is_available=data.get('is_available', False),
                title=data.get('title'),
                description=data.get('description'),
                start_time=data.get('start_time'),
                end_time=data.get('end_time')
            )
            
            db.session.add(exception)
            db.session.commit()
            
            return exception
            
        except Exception as e:
            current_app.logger.error(f"Error adding availability exception: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def delete_availability_exception(exception_id, user_id):
        """
        Delete an availability exception.
        
        Args:
            exception_id (int): The exception ID
            user_id (int): The user ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the exception
            exception = AvailabilityException.query.filter_by(
                id=exception_id,
                user_id=user_id
            ).first()
            
            if not exception:
                return False
            
            db.session.delete(exception)
            db.session.commit()
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error deleting availability exception: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_available_slots(user_id, date, duration_minutes=60):
        """
        Get available time slots for a specific date.
        
        Args:
            user_id (int): The user ID
            date (datetime): The date
            duration_minutes (int): The appointment duration in minutes
            
        Returns:
            list: List of available time slots
        """
        # Convert date to datetime objects for start and end of day
        start_date = datetime.combine(date.date(), time.min)
        end_date = datetime.combine(date.date(), time.max)
        
        # Get availability for the day
        availability = AvailabilityService.get_user_availability(user_id, start_date, end_date)
        
        if not availability or not availability['days']:
            return []
        
        # Get the day's availability
        day_availability = availability['days'][0]
        
        # Get available slots and appointments
        available_slots = day_availability['available_slots']
        existing_appointments = day_availability['appointments']
        
        # If no available slots, return empty list
        if not available_slots:
            return []
        
        # Convert appointments to unavailable time ranges
        unavailable_ranges = []
        
        for appointment in existing_appointments:
            start_str = appointment['start_time']
            end_str = appointment['end_time']
            
            # Convert to minutes since midnight for easier calculation
            start_minutes = int(start_str.split(':')[0]) * 60 + int(start_str.split(':')[1])
            end_minutes = int(end_str.split(':')[0]) * 60 + int(end_str.split(':')[1])
            
            unavailable_ranges.append((start_minutes, end_minutes))
        
        # Add unavailable slots to the unavailable ranges
        for slot in day_availability['unavailable_slots']:
            start_str = slot['start_time']
            end_str = slot['end_time']
            
            # Convert to minutes since midnight
            start_minutes = int(start_str.split(':')[0]) * 60 + int(start_str.split(':')[1])
            end_minutes = int(end_str.split(':')[0]) * 60 + int(end_str.split(':')[1])
            
            unavailable_ranges.append((start_minutes, end_minutes))
        
        # Sort unavailable ranges by start time
        unavailable_ranges.sort(key=lambda x: x[0])
        
        # Merge overlapping unavailable ranges
        merged_unavailable = []
        for start, end in unavailable_ranges:
            if not merged_unavailable or start > merged_unavailable[-1][1]:
                merged_unavailable.append((start, end))
            else:
                merged_unavailable[-1] = (merged_unavailable[-1][0], max(merged_unavailable[-1][1], end))
        
        # Calculate available time slots in each available slot
        available_times = []
        
        for slot in available_slots:
            start_str = slot['start_time']
            end_str = slot['end_time']
            
            # Convert to minutes since midnight
            slot_start = int(start_str.split(':')[0]) * 60 + int(start_str.split(':')[1])
            slot_end = int(end_str.split(':')[0]) * 60 + int(end_str.split(':')[1])
            
            # Generate potential start times at 15-minute intervals
            current_time = slot_start
            while current_time + duration_minutes <= slot_end:
                # Check if this time slot overlaps with any unavailable range
                is_available = True
                
                for unavail_start, unavail_end in merged_unavailable:
                    # Check if there's any overlap
                    if (current_time < unavail_end and current_time + duration_minutes > unavail_start):
                        is_available = False
                        break
                
                if is_available:
                    hours = current_time // 60
                    minutes = current_time % 60
                    end_time = current_time + duration_minutes
                    end_hours = end_time // 60
                    end_minutes = end_time % 60
                    
                    available_times.append({
                        'start_time': f"{hours:02d}:{minutes:02d}",
                        'end_time': f"{end_hours:02d}:{end_minutes:02d}",
                        'duration_minutes': duration_minutes
                    })
                
                # Move to next 15-minute increment
                current_time += 15
        
        return available_times