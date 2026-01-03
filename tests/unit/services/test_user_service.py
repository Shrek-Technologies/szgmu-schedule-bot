"""Unit tests for user service."""

from unittest.mock import AsyncMock, create_autospec

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.user_repo import UserRepository
from src.services.exceptions import UserNotFoundError
from src.services.user_service import UserService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    """Create mock UserRepository."""
    return create_autospec(UserRepository, instance=True)


@pytest.fixture
def user_service(mock_session: AsyncMock, mock_user_repo: AsyncMock) -> UserService:
    """Create UserService with mocked dependencies."""
    return UserService(session=mock_session, user_repo=mock_user_repo)


class TestUserService:
    """Tests for UserService."""

    @pytest.mark.asyncio
    async def test_get_or_create_user(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test get_or_create_user calls upsert and commits."""
        mock_user = AsyncMock(spec=User)
        mock_user.telegram_id = 12345
        mock_user_repo.upsert = AsyncMock(return_value=mock_user)

        result = await user_service.get_or_create_user(12345, "testuser", "Test User")

        mock_user_repo.upsert.assert_awaited_once_with(
            telegram_id=12345,
            username="testuser",
            full_name="Test User",
        )
        mock_session.commit.assert_awaited_once()
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_or_create_user_without_username(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test get_or_create_user with None username."""
        mock_user = AsyncMock(spec=User)
        mock_user_repo.upsert = AsyncMock(return_value=mock_user)

        result = await user_service.get_or_create_user(12345, None, "Test User")

        mock_user_repo.upsert.assert_awaited_once_with(
            telegram_id=12345,
            username=None,
            full_name="Test User",
        )
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_by_telegram_id(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test get_by_telegram_id delegates to repo."""
        mock_user = AsyncMock(spec=User)
        mock_user_repo.find_by_id = AsyncMock(return_value=mock_user)

        result = await user_service.get_by_telegram_id(12345)

        mock_user_repo.find_by_id.assert_awaited_once_with(12345)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_by_telegram_id_not_found(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test get_by_telegram_id returns None when not found."""
        mock_user_repo.find_by_id = AsyncMock(return_value=None)

        result = await user_service.get_by_telegram_id(12345)

        assert result is None

    @pytest.mark.asyncio
    async def test_set_user_subgroup_success(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test set_user_subgroup succeeds and commits."""
        mock_user_repo.update_subgroup = AsyncMock(return_value=True)

        result = await user_service.set_user_subgroup(12345, 5)

        mock_user_repo.update_subgroup.assert_awaited_once_with(12345, 5)
        mock_session.commit.assert_awaited_once()
        assert result is True

    @pytest.mark.asyncio
    async def test_set_user_subgroup_not_found(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test set_user_subgroup returns False when user not found."""
        mock_user_repo.update_subgroup = AsyncMock(return_value=False)

        result = await user_service.set_user_subgroup(12345, 5)

        assert result is False
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_set_user_subgroup_error_raises(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test set_user_subgroup raises UserNotFoundError on exception."""
        mock_user_repo.update_subgroup = AsyncMock(side_effect=ValueError("db error"))

        with pytest.raises(UserNotFoundError):
            await user_service.set_user_subgroup(12345, 5)

        mock_session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_set_user_subgroup_error_rolls_back(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test set_user_subgroup rolls back on error."""
        mock_user_repo.update_subgroup = AsyncMock(side_effect=RuntimeError("error"))

        with pytest.raises(UserNotFoundError):
            await user_service.set_user_subgroup(12345, 5)

        mock_session.rollback.assert_awaited_once()
