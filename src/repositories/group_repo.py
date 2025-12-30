from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from models.group import Group
from repositories.base import BaseRepository


class GroupRepository(BaseRepository):
    """Repository for group operations."""

    async def upsert(
        self,
        speciality_id: int,
        course_number: int,
        stream: str,
        name: str,
    ) -> Group:
        """Upsert a group based on unique constraint."""
        stmt = (
            insert(Group)
            .values(
                speciality_id=speciality_id,
                course_number=course_number,
                stream=stream,
                name=name,
            )
            .on_conflict_do_update(
                constraint="uq_groups_identity",
                set_={
                    "speciality_id": speciality_id,
                    "course_number": course_number,
                    "stream": stream,
                    "name": name,
                },
            )
            .returning(Group)
        )

        result = await self.session.execute(stmt)
        group = result.scalar_one()

        await self.session.refresh(group)
        return group

    async def find_by_id(self, group_id: int) -> Group | None:
        """Find group by ID with relationships loaded."""
        stmt = select(Group).where(Group.id == group_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_structure(
        self,
        speciality_id: int,
        course_number: int,
        stream: str,
        name: str,
    ) -> Group | None:
        """Find group by its complete structure with relationships loaded."""
        stmt = select(Group).where(
            Group.speciality_id == speciality_id,
            Group.course_number == course_number,
            Group.stream == stream,
            Group.name == name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_speciality_course_stream(
        self,
        speciality_id: int,
        course_number: int,
        stream: str,
    ) -> Sequence[Group]:
        """Find all groups for a specific speciality, course and stream."""
        stmt = (
            select(Group)
            .where(
                Group.speciality_id == speciality_id,
                Group.course_number == course_number,
                Group.stream == stream,
            )
            .order_by(Group.name)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_distinct_courses(self, speciality_id: int) -> Sequence[int]:
        """Find distinct course numbers for a speciality."""
        stmt = (
            select(Group.course_number)
            .where(Group.speciality_id == speciality_id)
            .distinct()
            .order_by(Group.course_number)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_distinct_streams(
        self,
        speciality_id: int,
        course_number: int,
    ) -> Sequence[str]:
        """Find distinct streams for a speciality and course."""
        stmt = (
            select(Group.stream)
            .where(
                Group.speciality_id == speciality_id,
                Group.course_number == course_number,
            )
            .distinct()
            .order_by(Group.stream)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
