class ServiceError(Exception):
    """Base exception for all service errors."""

    pass


class SyncError(ServiceError):
    """Raised when synchronization fails."""

    pass


class UserNotFoundError(ServiceError):
    """Raised when user is not found."""

    pass
