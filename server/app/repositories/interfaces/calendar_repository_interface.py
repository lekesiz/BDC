"""Calendar/Appointment repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.repositories.interfaces.base_repository_interface import IBaseRepository


class ICalendarRepository(IBaseRepository, ABC):
    """Interface for calendar/appointment repository operations."""
    
    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[Any]:
        """Find appointments by user ID.
        
        Args:
            user_id: User ID
            
        Returns:
            List of appointment instances
        """
        pass
    
    @abstractmethod
    def find_by_beneficiary_id(self, beneficiary_id: int) -> List[Any]:
        """Find appointments by beneficiary ID.
        
        Args:
            beneficiary_id: Beneficiary ID
            
        Returns:
            List of appointment instances
        """
        pass
    
    @abstractmethod
    def find_by_date_range(self, start_date: datetime, end_date: datetime, 
                          user_id: Optional[int] = None) -> List[Any]:
        """Find appointments by date range.
        
        Args:
            start_date: Start date
            end_date: End date
            user_id: Optional user ID filter
            
        Returns:
            List of appointment instances
        """
        pass
    
    @abstractmethod
    def find_by_status(self, status: str) -> List[Any]:
        """Find appointments by status.
        
        Args:
            status: Appointment status
            
        Returns:
            List of appointment instances
        """
        pass
    
    @abstractmethod
    def find_upcoming(self, user_id: Optional[int] = None, limit: int = 10) -> List[Any]:
        """Find upcoming appointments.
        
        Args:
            user_id: Optional user ID filter
            limit: Maximum number of results
            
        Returns:
            List of upcoming appointment instances
        """
        pass
    
    @abstractmethod
    def find_conflicts(self, start_time: datetime, end_time: datetime, 
                      user_id: int, exclude_id: Optional[int] = None) -> List[Any]:
        """Find conflicting appointments.
        
        Args:
            start_time: Start time
            end_time: End time
            user_id: User ID
            exclude_id: Appointment ID to exclude
            
        Returns:
            List of conflicting appointment instances
        """
        pass
    
    @abstractmethod
    def update_status(self, appointment_id: int, status: str) -> bool:
        """Update appointment status.
        
        Args:
            appointment_id: Appointment ID
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def reschedule(self, appointment_id: int, new_start_time: datetime, 
                  new_end_time: datetime) -> bool:
        """Reschedule appointment.
        
        Args:
            appointment_id: Appointment ID
            new_start_time: New start time
            new_end_time: New end time
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cancel(self, appointment_id: int, reason: Optional[str] = None) -> bool:
        """Cancel appointment.
        
        Args:
            appointment_id: Appointment ID
            reason: Cancellation reason
            
        Returns:
            True if successful, False otherwise
        """
        pass