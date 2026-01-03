"""Unit tests for sync service."""

from unittest.mock import AsyncMock, create_autospec

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.client import ScheduleAPIClient
from src.repositories.group_repo import GroupRepository
from src.repositories.lesson_repo import LessonRepository
from src.repositories.speciality_repo import SpecialityRepository
from src.repositories.subgroup_repo import SubgroupRepository
from src.services.exceptions import SyncError
from src.services.sync_service import SyncService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_api_client() -> AsyncMock:
    """Create mock API client."""
    return create_autospec(ScheduleAPIClient, instance=True)


@pytest.fixture
def mock_speciality_repo() -> AsyncMock:
    """Create mock SpecialityRepository."""
    return create_autospec(SpecialityRepository, instance=True)


@pytest.fixture
def mock_group_repo() -> AsyncMock:
    """Create mock GroupRepository."""
    return create_autospec(GroupRepository, instance=True)


@pytest.fixture
def mock_subgroup_repo() -> AsyncMock:
    """Create mock SubgroupRepository."""
    return create_autospec(SubgroupRepository, instance=True)


@pytest.fixture
def mock_lesson_repo() -> AsyncMock:
    """Create mock LessonRepository."""
    return create_autospec(LessonRepository, instance=True)


@pytest.fixture
def sync_service(
    mock_session: AsyncMock,
    mock_api_client: AsyncMock,
    mock_speciality_repo: AsyncMock,
    mock_group_repo: AsyncMock,
    mock_subgroup_repo: AsyncMock,
    mock_lesson_repo: AsyncMock,
) -> SyncService:
    """Create SyncService with mocked dependencies."""
    return SyncService(
        session=mock_session,
        api_client=mock_api_client,
        speciality_repo=mock_speciality_repo,
        group_repo=mock_group_repo,
        subgroup_repo=mock_subgroup_repo,
        lesson_repo=mock_lesson_repo,
    )


class TestSyncService:
    """Tests for SyncService."""

    @pytest.mark.asyncio
    async def test_sync_service_initialization(self, sync_service: SyncService) -> None:
        """Test SyncService is initialized correctly."""
        assert sync_service.session is not None
        assert sync_service.api_client is not None
        assert sync_service.speciality_repo is not None
        assert sync_service.group_repo is not None
        assert sync_service.subgroup_repo is not None
        assert sync_service.lesson_repo is not None

    @pytest.mark.asyncio
    async def test_sync_single_schedule_failure_fetch(
        self,
        sync_service: SyncService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Test sync_single_schedule raises error when fetch fails."""
        mock_api_client.get_schedule_details = AsyncMock(return_value=None)

        with pytest.raises(SyncError):
            await sync_service.sync_single_schedule(1)

    @pytest.mark.asyncio
    async def test_sync_single_schedule_calls_api(
        self,
        sync_service: SyncService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Test sync_single_schedule calls API client."""
        mock_detail = AsyncMock()
        mock_api_client.get_schedule_details = AsyncMock(return_value=mock_detail)

        with pytest.raises(Exception):
            # Will fail at parsing, but we test that API was called
            await sync_service.sync_single_schedule(1)

        mock_api_client.get_schedule_details.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_sync_all_schedules_empty(
        self,
        sync_service: SyncService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Test sync_all_schedules handles empty schedule list."""
        mock_api_client.get_all_schedules = AsyncMock(return_value=[])

        await sync_service.sync_all_schedules()

        mock_api_client.get_all_schedules.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_sync_all_schedules_error_propagates(
        self,
        sync_service: SyncService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Test sync_all_schedules propagates API errors."""
        mock_api_client.get_all_schedules = AsyncMock(side_effect=Exception("API error"))

        with pytest.raises(SyncError):
            await sync_service.sync_all_schedules()
