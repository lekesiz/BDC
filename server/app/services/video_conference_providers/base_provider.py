"""Base interface for video conference providers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class VideoConferenceProviderInterface(ABC):
    """Interface for video conference providers."""
    
    @abstractmethod
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a meeting with the provider.
        
        Args:
            meeting_data: Meeting configuration data
            
        Returns:
            Dict containing meeting_id, meeting_url, and provider-specific data
        """
        pass
    
    @abstractmethod
    def update_meeting(self, meeting_id: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a meeting with the provider.
        
        Args:
            meeting_id: Provider-specific meeting identifier
            meeting_data: Updated meeting data
            
        Returns:
            Dict containing update status and provider-specific data
        """
        pass
    
    @abstractmethod
    def delete_meeting(self, meeting_id: str) -> bool:
        """
        Delete a meeting with the provider.
        
        Args:
            meeting_id: Provider-specific meeting identifier
            
        Returns:
            bool: Success status
        """
        pass
    
    @abstractmethod
    def get_meeting_info(self, meeting_id: str) -> Dict[str, Any]:
        """
        Get meeting information from the provider.
        
        Args:
            meeting_id: Provider-specific meeting identifier
            
        Returns:
            Dict containing meeting information
        """
        pass
    
    @abstractmethod
    def start_recording(self, meeting_id: str) -> bool:
        """
        Start recording a meeting.
        
        Args:
            meeting_id: Provider-specific meeting identifier
            
        Returns:
            bool: Success status
        """
        pass
    
    @abstractmethod
    def stop_recording(self, meeting_id: str) -> bool:
        """
        Stop recording a meeting.
        
        Args:
            meeting_id: Provider-specific meeting identifier
            
        Returns:
            bool: Success status
        """
        pass
    
    @abstractmethod
    def get_recordings(self, meeting_id: str) -> List[Dict[str, Any]]:
        """
        Get recordings for a meeting.
        
        Args:
            meeting_id: Provider-specific meeting identifier
            
        Returns:
            List of recording information dictionaries
        """
        pass
    
    def add_participants(self, meeting_id: str, participants: List[Dict[str, Any]]) -> bool:
        """
        Add participants to a meeting.
        
        Args:
            meeting_id: Provider-specific meeting identifier
            participants: List of participant data
            
        Returns:
            bool: Success status
        """
        # Default implementation - override if provider supports it
        return True
    
    def remove_participant(self, meeting_id: str, participant_id: str) -> bool:
        """
        Remove a participant from a meeting.
        
        Args:
            meeting_id: Provider-specific meeting identifier
            participant_id: Provider-specific participant identifier
            
        Returns:
            bool: Success status
        """
        # Default implementation - override if provider supports it
        return True
    
    def get_meeting_participants(self, meeting_id: str) -> List[Dict[str, Any]]:
        """
        Get current meeting participants.
        
        Args:
            meeting_id: Provider-specific meeting identifier
            
        Returns:
            List of participant information dictionaries
        """
        # Default implementation - override if provider supports it
        return []
    
    def send_invitation(self, meeting_id: str, participants: List[Dict[str, Any]]) -> bool:
        """
        Send meeting invitations.
        
        Args:
            meeting_id: Provider-specific meeting identifier
            participants: List of participant data with email/contact info
            
        Returns:
            bool: Success status
        """
        # Default implementation - override if provider supports it
        return True
    
    def get_meeting_analytics(self, meeting_id: str) -> Dict[str, Any]:
        """
        Get meeting analytics and statistics.
        
        Args:
            meeting_id: Provider-specific meeting identifier
            
        Returns:
            Dict containing analytics data
        """
        # Default implementation - override if provider supports it
        return {}
    
    def validate_configuration(self) -> bool:
        """
        Validate provider configuration.
        
        Returns:
            bool: True if configuration is valid
        """
        # Default implementation - override for specific validation
        return True
    
    def get_provider_name(self) -> str:
        """
        Get the provider name.
        
        Returns:
            str: Provider name
        """
        return self.__class__.__name__.replace('Provider', '')
    
    def get_supported_features(self) -> List[str]:
        """
        Get list of supported features.
        
        Returns:
            List of supported feature names
        """
        return [
            'create_meeting',
            'update_meeting', 
            'delete_meeting',
            'get_meeting_info',
            'start_recording',
            'stop_recording',
            'get_recordings'
        ]
    
    def is_feature_supported(self, feature: str) -> bool:
        """
        Check if a feature is supported.
        
        Args:
            feature: Feature name to check
            
        Returns:
            bool: True if feature is supported
        """
        return feature in self.get_supported_features()


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class ProviderConfigurationError(ProviderError):
    """Exception for provider configuration errors."""
    pass


class ProviderAPIError(ProviderError):
    """Exception for provider API errors."""
    pass


class ProviderAuthenticationError(ProviderError):
    """Exception for provider authentication errors."""
    pass


class ProviderRateLimitError(ProviderError):
    """Exception for provider rate limit errors."""
    pass