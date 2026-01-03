"""Unit tests for schedule service."""

from datetime import date, timedelta
from unittest.mock import AsyncMock, create_autospec

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.lesson_repo import LessonRepository
from src.services.schedule_service import ScheduleService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_lesson_repo() -> AsyncMock:
    """Create mock LessonRepository."""
    return create_autospec(LessonRepository, instance=True)


@pytest.fixture
def schedule_service(mock_session: AsyncMock, mock_lesson_repo: AsyncMock) -> ScheduleService:
    """Create ScheduleService with mocked dependencies."""
    return ScheduleService(session=mock_session, lesson_repo=mock_lesson_repo)


class TestScheduleService:
    """Tests for ScheduleService."""

    @pytest.mark.asyncio
    async def test_get_schedule_for_date(
        self,
        schedule_service: ScheduleService,
        mock_lesson_repo: AsyncMock,
    ) -> None:
        """Test get_schedule_for_date calls repository."""
        target_date = date(2024, 9, 1)
        mock_lessons = []
        mock_lesson_repo.find_for_subgroup_on_date = AsyncMock(return_value=mock_lessons)

        result = await schedule_service.get_schedule_for_date(1, target_date)

        mock_lesson_repo.find_for_subgroup_on_date.assert_awaited_once_with(1, target_date)
        assert result == mock_lessons

    @pytest.mark.asyncio
    async def test_get_schedule_for_week(
        self,
        schedule_service: ScheduleService,
        mock_lesson_repo: AsyncMock,
    ) -> None:
        """Test get_schedule_for_week calls repository with correct date range."""
        week_start = date(2024, 9, 1)
        mock_lessons = []
        mock_lesson_repo.find_for_subgroup_in_range = AsyncMock(return_value=mock_lessons)

        result = await schedule_service.get_schedule_for_week(1, week_start)

        week_end = week_start + timedelta(days=6)
        mock_lesson_repo.find_for_subgroup_in_range.assert_awaited_once_with(
            1, week_start, week_end
        )
        assert result == mock_lessons

    @pytest.mark.asyncio
    async def test_get_today_schedule(
        self,
        schedule_service: ScheduleService,
        mock_lesson_repo: AsyncMock,
    ) -> None:
        """Test get_today_schedule retrieves today's schedule."""
        mock_lessons = []
        mock_lesson_repo.find_for_subgroup_on_date = AsyncMock(return_value=mock_lessons)

        result = await schedule_service.get_today_schedule(1)

        mock_lesson_repo.find_for_subgroup_on_date.assert_awaited_once()
        call_args = mock_lesson_repo.find_for_subgroup_on_date.call_args
        assert call_args[0][0] == 1
        assert isinstance(call_args[0][1], date)

    @pytest.mark.asyncio
    async def test_get_tomorrow_schedule(
        self,
        schedule_service: ScheduleService,
        mock_lesson_repo: AsyncMock,
    ) -> None:
        """Test get_tomorrow_schedule retrieves tomorrow's schedule."""
        mock_lessons = []
        mock_lesson_repo.find_for_subgroup_on_date = AsyncMock(return_value=mock_lessons)

        result = await schedule_service.get_tomorrow_schedule(1)

        mock_lesson_repo.find_for_subgroup_on_date.assert_awaited_once()
        call_args = mock_lesson_repo.find_for_subgroup_on_date.call_args
        assert call_args[0][0] == 1

    @pytest.mark.asyncio
    async def test_get_schedule_for_date_multiple_calls(
        self,
        schedule_service: ScheduleService,
        mock_lesson_repo: AsyncMock,
    ) -> None:
        """Test multiple get_schedule_for_date calls."""
        date1 = date(2024, 9, 1)
        date2 = date(2024, 9, 2)
        mock_lessons = []
        mock_lesson_repo.find_for_subgroup_on_date = AsyncMock(return_value=mock_lessons)

        await schedule_service.get_schedule_for_date(1, date1)
        await schedule_service.get_schedule_for_date(1, date2)

        assert mock_lesson_repo.find_for_subgroup_on_date.await_count == 2

    @pytest.mark.asyncio
    async def test_get_schedule_for_different_subgroups(
        self,
        schedule_service: ScheduleService,
        mock_lesson_repo: AsyncMock,
    ) -> None:
        """Test getting schedule for different subgroups."""
        target_date = date(2024, 9, 1)
        mock_lessons = []
        mock_lesson_repo.find_for_subgroup_on_date = AsyncMock(return_value=mock_lessons)

        await schedule_service.get_schedule_for_date(1, target_date)
        await schedule_service.get_schedule_for_date(2, target_date)

        calls = mock_lesson_repo.find_for_subgroup_on_date.await_args_list
        assert calls[0][0][0] == 1
        assert calls[1][0][0] == 2
