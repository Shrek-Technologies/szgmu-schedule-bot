"""Unit tests for API exceptions."""

import pytest

from src.api.exceptions import APIError, APINetworkError, APITimeoutError, APIValidationError


class TestAPIError:
    """Tests for APIError exception."""

    def test_api_error_is_exception(self) -> None:
        """Test APIError is an Exception."""
        error = APIError("api error")
        assert isinstance(error, Exception)

    def test_api_error_message(self) -> None:
        """Test APIError message."""
        error = APIError("test error message")
        assert str(error) == "test error message"

    def test_api_error_with_status_code(self) -> None:
        """Test APIError with status_code attribute."""
        error = APIError("error", status_code=500)
        assert error.status_code == 500  # type: ignore[attr-defined]

    def test_api_error_can_be_raised(self) -> None:
        """Test APIError can be raised and caught."""
        with pytest.raises(APIError):
            raise APIError("test error")


class TestAPINetworkError:
    """Tests for APINetworkError exception."""

    def test_api_network_error_is_api_error(self) -> None:
        """Test APINetworkError is an APIError."""
        error = APINetworkError("network error")
        assert isinstance(error, APIError)

    def test_api_network_error_message(self) -> None:
        """Test APINetworkError message."""
        error = APINetworkError("connection refused")
        assert str(error) == "connection refused"

    def test_api_network_error_can_be_raised(self) -> None:
        """Test APINetworkError can be raised and caught."""
        with pytest.raises(APINetworkError):
            raise APINetworkError("network error")

    def test_api_network_error_caught_as_api_error(self) -> None:
        """Test APINetworkError can be caught as APIError."""
        with pytest.raises(APIError):
            raise APINetworkError("network error")


class TestAPITimeoutError:
    """Tests for APITimeoutError exception."""

    def test_api_timeout_error_is_api_error(self) -> None:
        """Test APITimeoutError is an APIError."""
        error = APITimeoutError("timeout")
        assert isinstance(error, APIError)

    def test_api_timeout_error_message(self) -> None:
        """Test APITimeoutError message."""
        error = APITimeoutError("request timeout after 30 seconds")
        assert str(error) == "request timeout after 30 seconds"

    def test_api_timeout_error_can_be_raised(self) -> None:
        """Test APITimeoutError can be raised and caught."""
        with pytest.raises(APITimeoutError):
            raise APITimeoutError("timeout")

    def test_api_timeout_error_caught_as_api_error(self) -> None:
        """Test APITimeoutError can be caught as APIError."""
        with pytest.raises(APIError):
            raise APITimeoutError("timeout")


class TestAPIValidationError:
    """Tests for APIValidationError exception."""

    def test_api_validation_error_is_api_error(self) -> None:
        """Test APIValidationError is an APIError."""
        error = APIValidationError("validation failed")
        assert isinstance(error, APIError)

    def test_api_validation_error_message(self) -> None:
        """Test APIValidationError message."""
        error = APIValidationError("invalid response format")
        assert str(error) == "invalid response format"

    def test_api_validation_error_can_be_raised(self) -> None:
        """Test APIValidationError can be raised and caught."""
        with pytest.raises(APIValidationError):
            raise APIValidationError("validation failed")

    def test_api_validation_error_caught_as_api_error(self) -> None:
        """Test APIValidationError can be caught as APIError."""
        with pytest.raises(APIError):
            raise APIValidationError("validation failed")
