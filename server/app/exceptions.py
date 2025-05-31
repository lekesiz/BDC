"""Application exceptions module."""


class AppException(Exception):
    """Base exception for the application."""
    
    def __init__(self, message, status_code=400):
        """Initialize the exception."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
    
    def to_dict(self):
        """Convert exception to dictionary for API responses."""
        return {
            'error': self.__class__.__name__,
            'message': self.message
        }


class ValidationException(AppException):
    """Exception for validation errors."""
    
    def __init__(self, message):
        """Initialize the validation exception."""
        super().__init__(message, status_code=400)


class NotFoundException(AppException):
    """Exception for resource not found errors."""
    
    def __init__(self, message):
        """Initialize the not found exception."""
        super().__init__(message, status_code=404)


class UnauthorizedException(AppException):
    """Exception for unauthorized access."""
    
    def __init__(self, message):
        """Initialize the unauthorized exception."""
        super().__init__(message, status_code=401)


class ForbiddenException(AppException):
    """Exception for forbidden access."""
    
    def __init__(self, message):
        """Initialize the forbidden exception."""
        super().__init__(message, status_code=403)


class ConflictException(AppException):
    """Exception for conflict errors."""
    
    def __init__(self, message):
        """Initialize the conflict exception."""
        super().__init__(message, status_code=409)


class ExternalServiceException(AppException):
    """Exception for external service errors."""
    
    def __init__(self, message):
        """Initialize the external service exception."""
        super().__init__(message, status_code=503)