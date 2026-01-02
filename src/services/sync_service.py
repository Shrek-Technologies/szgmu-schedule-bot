import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.client import ScheduleAPIClient
from core.schedule_parser import ParsedGroupSchedule, ParsedSchedule, ScheduleParser
from repositories.group_repo import GroupRepository
from repositories.lesson_repo import LessonRepository
from repositories.speciality_repo import SpecialityRepository
from repositories.subgroup_repo import SubgroupRepository
from .exceptions import SyncError

logger = logging.getLogger(__name__)


class SyncService:
    """Service for synchronizing lessons from external API to database."""

    def __init__(
        self,
        session: AsyncSession,
        api_client: ScheduleAPIClient,
        speciality_repo: SpecialityRepository,
        group_repo: GroupRepository,
        subgroup_repo: SubgroupRepository,
        lesson_repo: LessonRepository,
    ) -> None:
        """Initialize SyncService.

        Args:
            session: AsyncSession for database operations
            api_client: Schedule API client
            speciality_repo: Speciality repository
            group_repo: Group repository
            subgroup_repo: Subgroup repository
            lesson_repo: Lesson repository
        """
        self.session = session
        self.api_client = api_client
        self.speciality_repo = speciality_repo
        self.group_repo = group_repo
        self.subgroup_repo = subgroup_repo
        self.lesson_repo = lesson_repo

    async def sync_single_schedule(self, schedule_id: int) -> None:
        """Synchronize a single schedule.

        Args:
            schedule_id: ID of the schedule to sync

        Raises:
            SyncError: If synchronization fails
        """
        schedule_detail = await self.api_client.get_schedule_details(schedule_id)
        if schedule_detail is None:
            raise SyncError("Failed to fetch schedule %d", schedule_id)

        try:
            parsed = ScheduleParser.parse(schedule_detail)
            await self._persist_schedule(parsed)
            await self.session.commit()
            logger.info("Successfully synced schedule %d", schedule_id)

        except Exception as e:
            await self.session.rollback()
            raise SyncError(f"Error syncing schedule {schedule_id}: {e!s}") from e

    async def sync_all_schedules(self) -> None:
        """Synchronize all available schedules.

        Handles partial failures by logging and continuing with remaining schedules.
        """
        try:
            summaries = await self.api_client.get_all_schedules()
            logger.info("Found %d schedules to sync", len(summaries))

            failed_schedules = []

            for summary in summaries:
                try:
                    await self.sync_single_schedule(summary.id)
                except SyncError as e:
                    failed_schedules.append((summary.id, str(e)))
                    logger.error("Error syncing schedule %d: %s", summary.id, e)

            logger.info("Sync completed. Failed schedules: %d", len(failed_schedules))

            if failed_schedules:
                for schedule_id, error in failed_schedules:
                    logger.error("  - Schedule %d: %s", schedule_id, error)

        except Exception as e:
            raise SyncError(f"Error during sync_all_schedules: {e!s}") from e

    async def _persist_schedule(self, parsed: ParsedSchedule) -> None:
        """Persist parsed schedule to database.

        Args:
            parsed: ParsedSchedule from ScheduleParser
        """
        for group in parsed.groups:
            await self._persist_group(group)

    async def _persist_group(self, group: ParsedGroupSchedule) -> None:
        """Persist a single parsed group to database.

        Args:
            group: ParsedGroupSchedule
        """
        speciality = await self.speciality_repo.upsert(
            code=group.speciality_code,
            full_name=group.speciality_full_name,
            clean_name=group.speciality_clean_name,
            level=group.speciality_level,
        )

        group_entity = await self.group_repo.upsert(
            speciality_id=speciality.id,
            course_number=group.course_number,
            stream=group.stream,
            name=group.group_name,
        )

        subgroup = await self.subgroup_repo.upsert(
            group_id=group_entity.id,
            name=group.subgroup_name,
        )

        # Prepare lessons data for bulk upsert
        lessons_data = [
            {
                "subgroup_id": subgroup.id,
                "subject": lesson.subject,
                "lesson_type": lesson.lesson_type,
                "date": lesson.date,
                "start_time": lesson.start_time,
                "end_time": lesson.end_time,
                "teacher": lesson.teacher,
                "address": lesson.address,
                "room": lesson.room,
            }
            for lesson in group.lessons
        ]

        if lessons_data:
            await self.lesson_repo.bulk_upsert(lessons_data)
