"""Unit tests for API client."""

from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientError

from src.api.base_client import BaseAPIClient
from src.api.exceptions import APINetworkError, APITimeoutError


class TestBaseAPIClient:
    """Tests for BaseAPIClient."""

    BASE_URL = "https://example.com/api"

    def test_base_api_client_initialization(self) -> None:
        """Test client initialization with defaults."""
        client = BaseAPIClient(base_url="https://api.example.com")
        assert client.base_url == "https://api.example.com"
        assert client.timeout.total == 30.0
        assert client.max_retries == 3
        assert client.retry_delay == 1.0

    def test_base_api_client_custom_initialization(self) -> None:
        """Test client initialization with custom parameters."""
        client = BaseAPIClient(
            base_url="https://api.example.com",
            timeout=60.0,
            max_retries=5,
            retry_delay=2.0,
        )
        assert client.timeout.total == 60.0
        assert client.max_retries == 5
        assert client.retry_delay == 2.0

    def test_base_api_client_base_url_normalization(self) -> None:
        """Test base URL is normalized (trailing slash removed)."""
        client = BaseAPIClient(base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"

    def test_build_url_from_endpoint(self) -> None:
        """Test URL building from endpoint."""
        client = BaseAPIClient(base_url="https://api.example.com")
        url = client._build_url("/schedule/groups")
        assert url == "https://api.example.com/schedule/groups"

    def test_build_url_without_leading_slash(self) -> None:
        """Test URL building handles missing leading slash."""
        client = BaseAPIClient(base_url="https://api.example.com")
        url = client._build_url("schedule/groups")
        assert url == "https://api.example.com/schedule/groups"

    @pytest.mark.asyncio
    async def test_context_manager_setup(self) -> None:
        """Test async context manager setup."""
        client = BaseAPIClient(base_url="https://api.example.com")
        async with client as ctx:
            assert ctx is client
            assert client._session is not None

    @pytest.mark.asyncio
    async def test_context_manager_cleanup(self) -> None:
        """Test async context manager cleanup."""
        client = BaseAPIClient(base_url="https://api.example.com")
        async with client as ctx:
            session = ctx._session
        assert session is not None
        assert session.closed

    @pytest.mark.asyncio
    async def test_ensure_session_creates_session(self) -> None:
        """Test _ensure_session creates a ClientSession."""
        client = BaseAPIClient(base_url="https://api.example.com")
        session = await client._ensure_session()
        assert session is not None
        await client.close()

    @pytest.mark.asyncio
    async def test_ensure_session_reuses_session(self) -> None:
        """Test _ensure_session reuses existing session."""
        client = BaseAPIClient(base_url="https://api.example.com")
        session1 = await client._ensure_session()
        session2 = await client._ensure_session()
        assert session1 is session2
        await client.close()

    @pytest.mark.asyncio
    async def test_close_closes_session(self) -> None:
        """Test close method closes session."""
        client = BaseAPIClient(base_url="https://api.example.com")
        await client._ensure_session()
        await client.close()
        assert client._session is not None
        assert client._session.closed

    @pytest.mark.asyncio
    async def test_close_without_session(self) -> None:
        """Test close works when session not initialized."""
        client = BaseAPIClient(base_url="https://api.example.com")
        await client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_get_method(self) -> None:
        """Test GET request method."""
        client = BaseAPIClient(base_url="https://api.example.com")
        mock_response = {"status": "ok"}

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock:
            mock.return_value = mock_response
            result = await client.get("/schedule")
            mock.assert_awaited_once_with("GET", "/schedule", params=None)
            assert result == mock_response

        await client.close()

    @pytest.mark.asyncio
    async def test_post_method(self) -> None:
        """Test POST request method."""
        client = BaseAPIClient(base_url="https://api.example.com")
        request_data = {"filter": "test"}
        response_data = {"result": []}

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock:
            mock.return_value = response_data
            result = await client.post("/schedule", json=request_data)
            mock.assert_awaited_once()
            assert result == response_data

        await client.close()


class TestBaseAPIClientRetry:
    """Tests for retry logic in BaseAPIClient."""

    @pytest.mark.asyncio
    async def test_request_retry_on_timeout(self) -> None:
        """Test retry on timeout error."""
        client = BaseAPIClient(base_url="https://api.example.com", max_retries=2)

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock:
            mock.side_effect = TimeoutError("timeout")
            with pytest.raises(APITimeoutError):
                await client._request_with_retry("GET", "/schedule")

        assert mock.await_count == 3

        await client.close()

    @pytest.mark.asyncio
    async def test_request_retry_success_on_second_attempt(self) -> None:
        """Test request succeeds on second attempt."""
        client = BaseAPIClient(base_url="https://api.example.com", max_retries=3)

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock:
            mock.side_effect = [ClientError("error"), {"status": "ok"}]
            result = await client._request_with_retry("GET", "/schedule")

        assert result == {"status": "ok"}
        assert mock.await_count == 2

        await client.close()

    @pytest.mark.asyncio
    async def test_request_retry_max_attempts(self) -> None:
        """Test retry stops at max_retries."""
        client = BaseAPIClient(base_url="https://api.example.com", max_retries=3)

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock:
            mock.side_effect = ClientError("error")
            with pytest.raises(APINetworkError):
                await client._request_with_retry("GET", "/schedule")

        assert mock.await_count == 4

        await client.close()


class TestBaseAPIClientExceptions:
    """Tests for exception handling."""

    @pytest.mark.asyncio
    async def test_timeout_raises_api_timeout_error(self) -> None:
        """Test timeout raises APITimeoutError."""
        client = BaseAPIClient(base_url="https://api.example.com", max_retries=1)

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock:
            mock.side_effect = TimeoutError("timeout")
            with pytest.raises(APITimeoutError):
                await client._request_with_retry("GET", "/schedule")

        await client.close()

    @pytest.mark.asyncio
    async def test_client_error_raises_api_network_error(self) -> None:
        """Test ClientError raises APINetworkError."""
        client = BaseAPIClient(base_url="https://api.example.com", max_retries=1)

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock:
            mock.side_effect = ClientError("network error")
            with pytest.raises(APINetworkError):
                await client._request_with_retry("GET", "/schedule")

        await client.close()
