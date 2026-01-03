"""Unit tests for DI container."""

import pytest
from dishka import AsyncContainer

from src.di.container import create_container


class TestDiContainer:
    """Tests for DI container creation."""

    def test_create_container_returns_async_container(self) -> None:
        """Test create_container returns AsyncContainer."""
        container = create_container()
        assert isinstance(container, AsyncContainer)

    def test_create_container_is_not_none(self) -> None:
        """Test create_container returns non-None container."""
        container = create_container()
        assert container is not None

    @pytest.mark.asyncio
    async def test_container_can_be_closed(self) -> None:
        """Test container can be closed."""
        container = create_container()
        await container.close()
        # Should not raise

    def test_multiple_container_calls_create_different_instances(self) -> None:
        """Test multiple calls to create_container create different instances."""
        container1 = create_container()
        container2 = create_container()
        assert container1 is not container2
