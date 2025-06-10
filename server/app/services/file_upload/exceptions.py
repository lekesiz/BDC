"""Custom exceptions for file upload system."""


class FileUploadException(Exception):
    """Base exception for file upload system."""
    pass


class FileTypeNotAllowedException(FileUploadException):
    """Raised when file type is not allowed."""
    pass


class FileSizeExceededException(FileUploadException):
    """Raised when file size exceeds limit."""
    pass


class VirusDetectedException(FileUploadException):
    """Raised when virus is detected in file."""
    pass


class FileScanException(FileUploadException):
    """Raised when file scanning fails."""
    pass


class ImageProcessingException(FileUploadException):
    """Raised when image processing fails."""
    pass


class StorageException(FileUploadException):
    """Raised when storage operations fail."""
    pass


class EncryptionException(FileUploadException):
    """Raised when encryption/decryption fails."""
    pass


class VersioningException(FileUploadException):
    """Raised when file versioning fails."""
    pass


class AuditException(FileUploadException):
    """Raised when audit logging fails."""
    pass