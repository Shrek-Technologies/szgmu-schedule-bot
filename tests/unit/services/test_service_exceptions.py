"""Unit tests for service exceptions."""

import pytest

from src.services.exceptions import ServiceError, SyncError, UserNotFoundError


class TestServiceError:
    """Tests for ServiceError exception."""

    def test_service_error_is_exception(self) -> None:
        """Test ServiceError is an Exception."""
        error = ServiceError("test error")
        assert isinstance(error, Exception)

    def test_service_error_message(self) -> None:
        """Test ServiceError message."""
        error = ServiceError("test error message")
        assert str(error) == "test error message"

    def test_service_error_can_be_raised(self) -> None:
        """Test ServiceError can be raised and caught."""
        with pytest.raises(ServiceError):
            raise ServiceError("test error")


class TestSyncError:
    """Tests for SyncError exception."""

    def test_sync_error_is_service_error(self) -> None:
        """Test SyncError is a ServiceError."""
        error = SyncError("sync failed")
        assert isinstance(error, ServiceError)

    def test_sync_error_message(self) -> None:
        """Test SyncError message."""
        error = SyncError("sync failed message")
        assert str(error) == "sync failed message"

    def test_sync_error_can_be_raised(self) -> None:
        """Test SyncError can be raised and caught."""
        with pytest.raises(SyncError):
            raise SyncError("sync failed")

    def test_sync_error_caught_as_service_error(self) -> None:
        """Test SyncError can be caught as ServiceError."""
        with pytest.raises(ServiceError):
            raise SyncError("sync failed")


class TestUserNotFoundError:
    """Tests for UserNotFoundError exception."""

    def test_user_not_found_error_is_service_error(self) -> None:
        """Test UserNotFoundError is a ServiceError."""
        error = UserNotFoundError("user not found")
        assert isinstance(error, ServiceError)

    def test_user_not_found_error_message(self) -> None:
        """Test UserNotFoundError message."""
        error = UserNotFoundError("user 123 not found")
        assert str(error) == "user 123 not found"

    def test_user_not_found_error_can_be_raised(self) -> None:
        """Test UserNotFoundError can be raised and caught."""
        with pytest.raises(UserNotFoundError):
            raise UserNotFoundError("user not found")

    def test_user_not_found_error_caught_as_service_error(self) -> None:
        """Test UserNotFoundError can be caught as ServiceError."""
        with pytest.raises(ServiceError):
            raise UserNotFoundError("user not found")
