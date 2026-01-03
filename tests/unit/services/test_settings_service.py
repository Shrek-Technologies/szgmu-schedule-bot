"""Unit tests for settings service."""

from datetime import time
from unittest.mock import AsyncMock, create_autospec

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user_repo import UserRepository
from src.services.settings_service import SettingsService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    """Create mock UserRepository."""
    return create_autospec(UserRepository, instance=True)


@pytest.fixture
def settings_service(mock_session: AsyncMock, mock_user_repo: AsyncMock) -> SettingsService:
    """Create SettingsService with mocked dependencies."""
    return SettingsService(session=mock_session, user_repo=mock_user_repo)


class TestSettingsService:
    """Tests for SettingsService."""

    @pytest.mark.asyncio
    async def test_toggle_notifications_enable(
        self,
        settings_service: SettingsService,
        mock_user_repo: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test toggle_notifications enables notifications."""
        mock_user_repo.update_subscription = AsyncMock(return_value=True)

        result = await settings_service.toggle_notifications(12345, True)

        mock_user_repo.update_subscription.assert_awaited_once_with(12345, True)
        mock_session.commit.assert_awaited_once()
        assert result is True

    @pytest.mark.asyncio
    async def test_toggle_notifications_disable(
        self,
        settings_service: SettingsService,
        mock_user_repo: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test toggle_notifications disables notifications."""
        mock_user_repo.update_subscription = AsyncMock(return_value=True)

        result = await settings_service.toggle_notifications(12345, False)

        mock_user_repo.update_subscription.assert_awaited_once_with(12345, False)
        assert result is True

    @pytest.mark.asyncio
    async def test_toggle_notifications_user_not_found(
        self,
        settings_service: SettingsService,
        mock_user_repo: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test toggle_notifications returns False when user not found."""
        mock_user_repo.update_subscription = AsyncMock(return_value=False)

        result = await settings_service.toggle_notifications(99999, True)

        assert result is False

    @pytest.mark.asyncio
    async def test_set_notification_time(
        self,
        settings_service: SettingsService,
        mock_user_repo: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test set_notification_time updates time."""
        target_time = time(8, 30)
        mock_user_repo.update_notification_time = AsyncMock(return_value=True)

        result = await settings_service.set_notification_time(12345, target_time)

        mock_user_repo.update_notification_time.assert_awaited_once_with(12345, target_time)
        mock_session.commit.assert_awaited_once()
        assert result is True

    @pytest.mark.asyncio
    async def test_set_notification_time_various_times(
        self,
        settings_service: SettingsService,
        mock_user_repo: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test set_notification_time with various times."""
        times_to_test = [
            time(7, 0),
            time(12, 0),
            time(19, 30),
            time(23, 59),
        ]

        mock_user_repo.update_notification_time = AsyncMock(return_value=True)

        for target_time in times_to_test:
            await settings_service.set_notification_time(12345, target_time)
            mock_user_repo.update_notification_time.assert_awaited_with(12345, target_time)

    @pytest.mark.asyncio
    async def test_set_notification_time_user_not_found(
        self,
        settings_service: SettingsService,
        mock_user_repo: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test set_notification_time returns False when user not found."""
        mock_user_repo.update_notification_time = AsyncMock(return_value=False)

        result = await settings_service.set_notification_time(99999, time(8, 0))

        assert result is False

    @pytest.mark.asyncio
    async def test_get_users_for_notification_batch(
        self,
        settings_service: SettingsService,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test get_users_for_notification_batch retrieves users."""
        mock_users = []
        target_time = time(8, 0)
        mock_user_repo.find_subscribed_users_by_time = AsyncMock(return_value=mock_users)

        result = await settings_service.get_users_for_notification_batch(target_time)

        mock_user_repo.find_subscribed_users_by_time.assert_awaited_once_with(target_time)
        assert result == mock_users

    @pytest.mark.asyncio
    async def test_get_users_for_notification_batch_returns_sequence(
        self,
        settings_service: SettingsService,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test get_users_for_notification_batch returns sequence."""
        mock_users = []
        mock_user_repo.find_subscribed_users_by_time = AsyncMock(return_value=mock_users)

        result = await settings_service.get_users_for_notification_batch(time(8, 0))

        assert isinstance(result, (list, tuple))
