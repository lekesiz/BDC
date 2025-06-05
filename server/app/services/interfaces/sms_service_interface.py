"""SMS service interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime


class ISMSService(ABC):
    """Interface for SMS service operations."""
    
    @abstractmethod
    def send_sms(
        self,
        phone_number: str,
        message: str,
        message_type: str = 'general_notification',
        user_id: Optional[int] = None,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None,
        tenant_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Send an SMS message.
        
        Returns:
            Tuple of (success, message_id, response_data)
        """
        pass
    
    @abstractmethod
    def send_templated_sms(
        self,
        phone_number: str,
        template_id: str,
        variables: Optional[Dict[str, Any]] = None,
        message_type: str = 'general_notification',
        user_id: Optional[int] = None,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None,
        tenant_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Send an SMS using a template.
        
        Returns:
            Tuple of (success, message_id, response_data)
        """
        pass
    
    @abstractmethod
    def send_bulk_sms(
        self,
        phone_numbers: List[str],
        message: str,
        message_type: str = 'general_notification',
        tenant_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Send SMS to multiple recipients.
        
        Returns:
            Dict with success count, failed count, and details
        """
        pass
    
    @abstractmethod
    def schedule_sms(
        self,
        phone_number: str,
        message: str,
        scheduled_time: datetime,
        message_type: str = 'general_notification',
        user_id: Optional[int] = None,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None,
        tenant_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[int]]:
        """
        Schedule an SMS for future delivery.
        
        Returns:
            Tuple of (success, scheduled_message_id)
        """
        pass
    
    @abstractmethod
    def cancel_scheduled_sms(self, message_id: int) -> bool:
        """
        Cancel a scheduled SMS.
        
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    def get_sms_status(self, message_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the status of an SMS message.
        
        Returns:
            Message status details or None
        """
        pass
    
    @abstractmethod
    def get_sms_history(
        self,
        user_id: Optional[int] = None,
        phone_number: Optional[str] = None,
        message_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get SMS history with filters.
        
        Returns:
            List of SMS messages
        """
        pass
    
    @abstractmethod
    def get_sms_stats(
        self,
        tenant_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get SMS statistics.
        
        Returns:
            Statistics including counts, costs, etc.
        """
        pass
    
    @abstractmethod
    def validate_phone_number(self, phone_number: str, country_code: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate and format a phone number.
        
        Returns:
            Tuple of (is_valid, formatted_number)
        """
        pass
    
    @abstractmethod
    def send_appointment_reminder(
        self,
        appointment_id: int,
        phone_number: str,
        user_id: Optional[int] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str]]:
        """
        Send appointment reminder SMS.
        
        Returns:
            Tuple of (success, message_id)
        """
        pass
    
    @abstractmethod
    def send_assessment_notification(
        self,
        assessment_id: int,
        phone_number: str,
        user_id: Optional[int] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str]]:
        """
        Send assessment notification SMS.
        
        Returns:
            Tuple of (success, message_id)
        """
        pass
    
    @abstractmethod
    def send_password_reset_code(
        self,
        phone_number: str,
        reset_code: str,
        user_id: Optional[int] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str]]:
        """
        Send password reset code via SMS.
        
        Returns:
            Tuple of (success, message_id)
        """
        pass
    
    @abstractmethod
    def send_2fa_code(
        self,
        phone_number: str,
        auth_code: str,
        user_id: Optional[int] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str]]:
        """
        Send 2FA verification code via SMS.
        
        Returns:
            Tuple of (success, message_id)
        """
        pass
    
    @abstractmethod
    def create_sms_campaign(
        self,
        name: str,
        template_id: Optional[str] = None,
        message_content: Optional[str] = None,
        recipient_filters: Optional[Dict[str, Any]] = None,
        scheduled_for: Optional[datetime] = None,
        tenant_id: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> Optional[int]:
        """
        Create an SMS campaign.
        
        Returns:
            Campaign ID or None
        """
        pass
    
    @abstractmethod
    def execute_sms_campaign(self, campaign_id: int) -> bool:
        """
        Execute an SMS campaign.
        
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    def get_campaign_status(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        """
        Get campaign status and statistics.
        
        Returns:
            Campaign details or None
        """
        pass