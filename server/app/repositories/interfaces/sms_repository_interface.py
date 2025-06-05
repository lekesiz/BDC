"""SMS repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime


class ISMSRepository(ABC):
    """Interface for SMS repository operations."""
    
    @abstractmethod
    def create(self, **kwargs) -> Optional[Any]:
        """Create a new SMS message record."""
        pass
    
    @abstractmethod
    def get(self, message_id: int) -> Optional[Any]:
        """Get an SMS message by ID."""
        pass
    
    @abstractmethod
    def update(self, message_id: int, **kwargs) -> bool:
        """Update an SMS message."""
        pass
    
    @abstractmethod
    def delete(self, message_id: int) -> bool:
        """Delete an SMS message."""
        pass
    
    @abstractmethod
    def get_by_status(self, status: str, limit: int = 100) -> List[Any]:
        """Get SMS messages by status."""
        pass
    
    @abstractmethod
    def get_scheduled_messages(self, before_time: datetime) -> List[Any]:
        """Get scheduled messages that need to be sent."""
        pass
    
    @abstractmethod
    def get_user_messages(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[Any]:
        """Get SMS messages for a specific user."""
        pass
    
    @abstractmethod
    def get_by_phone(
        self,
        phone_number: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Any]:
        """Get SMS messages by phone number."""
        pass
    
    @abstractmethod
    def get_by_campaign(self, campaign_id: int) -> List[Any]:
        """Get SMS messages for a specific campaign."""
        pass
    
    @abstractmethod
    def count_by_status(self, status: str, start_date: Optional[datetime] = None) -> int:
        """Count SMS messages by status."""
        pass
    
    @abstractmethod
    def get_cost_summary(
        self,
        tenant_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get cost summary for SMS messages."""
        pass