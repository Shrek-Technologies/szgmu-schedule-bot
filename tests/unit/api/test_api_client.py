"""Unit tests for API client."""

import pytest

from src.api.client import ScheduleAPIClient


class TestScheduleAPIClient:
    """Tests for ScheduleAPIClient."""

    def test_schedule_api_client_initialization(self) -> None:
        """Test ScheduleAPIClient initialization."""
        client = ScheduleAPIClient(base_url="https://api.example.com", timeout=30)
        assert client.base_url == "https://api.example.com"

    @pytest.mark.asyncio
    async def test_schedule_api_client_close(self) -> None:
        """Test ScheduleAPIClient can be closed."""
        client = ScheduleAPIClient(base_url="https://api.example.com")
        await client.close()
        # Should not raise

    @pytest.mark.asyncio
    async def test_schedule_api_client_context_manager(self) -> None:
        """Test ScheduleAPIClient works as async context manager."""
        async with ScheduleAPIClient(base_url="https://api.example.com") as client:
            assert client is not None
