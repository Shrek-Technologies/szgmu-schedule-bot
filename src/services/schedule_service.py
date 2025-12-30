import logging
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from models.lesson import Lesson
from repositories.lesson_repo import LessonRepository

logger = logging.getLogger(__name__)


class ScheduleService:
    """Service for retrieving lesson schedules."""

    def __init__(
        self,
        session: AsyncSession,
        lesson_repo: LessonRepository,
    ) -> None:
        """Initialize ScheduleService with repository.

        Args:
            session: AsyncSession for database operations
            lesson_repo: Repository for lessons
        """
        self.session = session
        self.lesson_repo = lesson_repo

    async def get_schedule_for_date(self, subgroup_id: int, target_date: date) -> list[Lesson]:
        """Get all lessons for a subgroup on a specific date.

        Args:
            subgroup_id: ID of the subgroup
            target_date: Date to retrieve lessons for

        Returns:
            List of Lesson objects sorted by start_time
        """
        return await self.lesson_repo.find_for_subgroup_on_date(subgroup_id, target_date)

    async def get_schedule_for_week(self, subgroup_id: int, week_start_date: date) -> list[Lesson]:
        """Get all lessons for a subgroup in a week starting from a date.

        Args:
            subgroup_id: ID of the subgroup
            week_start_date: Date to start the week from

        Returns:
            List of Lesson objects sorted by date and start_time
        """
        week_end_date = week_start_date + timedelta(days=6)
        return await self.lesson_repo.find_for_subgroup_in_range(
            subgroup_id, week_start_date, week_end_date
        )

    async def get_today_schedule(self, subgroup_id: int) -> list[Lesson]:
        """Get all lessons for a subgroup today.

        Args:
            subgroup_id: ID of the subgroup

        Returns:
            List of Lesson objects sorted by start_time
        """
        today = date.today()
        return await self.get_schedule_for_date(subgroup_id, today)

    async def get_tomorrow_schedule(self, subgroup_id: int) -> list[Lesson]:
        """Get all lessons for a subgroup tomorrow.

        Args:
            subgroup_id: ID of the subgroup

        Returns:
            List of Lesson objects sorted by start_time
        """
        tomorrow = date.today() + timedelta(days=1)
        return await self.get_schedule_for_date(subgroup_id, tomorrow)
