import logging
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from models.group import Group
from models.speciality import Speciality
from models.subgroup import Subgroup
from repositories.group_repo import GroupRepository
from repositories.speciality_repo import SpecialityRepository
from repositories.subgroup_repo import SubgroupRepository

logger = logging.getLogger(__name__)


class GroupSelectionService:
    """Service for hierarchical group selection.

    Provides step-by-step data retrieval for user onboarding questionnaire:
    speciality -> course -> stream -> group -> subgroup.
    """

    def __init__(
        self,
        session: AsyncSession,
        speciality_repo: SpecialityRepository,
        group_repo: GroupRepository,
        subgroup_repo: SubgroupRepository,
    ) -> None:
        """Initialize GroupSelectionService with repositories.

        Args:
            session: AsyncSession for database operations
            speciality_repo: Repository for specialities
            group_repo: Repository for groups
            subgroup_repo: Repository for subgroups
        """
        self.session = session
        self.speciality_repo = speciality_repo
        self.group_repo = group_repo
        self.subgroup_repo = subgroup_repo

    async def get_all_specialities(self) -> Sequence[Speciality]:
        """Get all available specialities.

        Returns:
            Sequence of Speciality objects
        """
        return await self.speciality_repo.find_all()

    async def get_courses_by_speciality(self, speciality_id: int) -> Sequence[int]:
        """Get all distinct course numbers for a speciality.

        Args:
            speciality_id: ID of the speciality

        Returns:
            Sorted sequence of course numbers
        """
        return await self.group_repo.find_distinct_courses(speciality_id)

    async def get_streams_by_speciality_course(
        self, speciality_id: int, course_number: int
    ) -> Sequence[str]:
        """Get all distinct streams for a speciality and course.

        Args:
            speciality_id: ID of the speciality
            course_number: Course number

        Returns:
            Sequence of stream identifiers
        """
        return await self.group_repo.find_distinct_streams(speciality_id, course_number)

    async def get_groups_by_structure(
        self, speciality_id: int, course_number: int, stream: str
    ) -> Sequence[Group]:
        """Get all groups matching the speciality, course, and stream.

        Args:
            speciality_id: ID of the speciality
            course_number: Course number
            stream: Stream identifier

        Returns:
            Sequence of Group objects
        """
        return await self.group_repo.find_by_speciality_course_stream(
            speciality_id, course_number, stream
        )

    async def get_subgroups_by_group(self, group_id: int) -> Sequence[Subgroup]:
        """Get all subgroups for a group.

        Args:
            group_id: ID of the group

        Returns:
            Sequence of Subgroup objects
        """
        return await self.subgroup_repo.find_by_group(group_id)
