class ServiceError(Exception):
    """Base exception for all service errors."""


class SyncError(ServiceError):
    """Raised when synchronization fails."""


class UserNotFoundError(ServiceError):
    """Raised when user is not found."""
