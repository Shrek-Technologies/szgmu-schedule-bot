from collections.abc import Sequence
from datetime import date, time

from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert

from models.lesson import Lesson, LessonType
from repositories.base import BaseRepository


class LessonRepository(BaseRepository):
    """Repository for lesson operations."""

    async def upsert(
        self,
        subgroup_id: int,
        subject: str,
        lesson_type: LessonType,
        date: date,
        start_time: time,
        end_time: time,
        teacher: str | None = None,
        address: str | None = None,
        room: str | None = None,
    ) -> Lesson:
        """Upsert a lesson based on unique constraint."""
        stmt = (
            insert(Lesson)
            .values(
                subgroup_id=subgroup_id,
                subject=subject,
                lesson_type=lesson_type,
                date=date,
                start_time=start_time,
                end_time=end_time,
                teacher=teacher,
                address=address,
                room=room,
            )
            .on_conflict_do_update(
                constraint="uq_lesson_unique",
                set_={
                    "subject": subject,
                    "lesson_type": lesson_type,
                    "teacher": teacher,
                    "address": address,
                    "room": room,
                },
            )
            .returning(Lesson)
        )

        result = await self.session.execute(stmt)
        lesson = result.scalar_one()

        await self.session.refresh(lesson)
        return lesson

    async def bulk_upsert(self, lessons_data: Sequence[dict]) -> Sequence[Lesson]:
        """Bulk upsert lessons."""
        if not lessons_data:
            return []

        stmt = insert(Lesson).values(lessons_data)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_lesson_unique",
            set_={
                "end_time": stmt.excluded.end_time,
                "teacher": stmt.excluded.teacher,
                "lesson_type": stmt.excluded.lesson_type,
                "address": stmt.excluded.address,
                "room": stmt.excluded.room,
            },
        ).returning(Lesson)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_for_subgroup_on_date(
        self,
        subgroup_id: int,
        lesson_date: date,
    ) -> Sequence[Lesson]:
        """Find lessons for a subgroup on a specific date."""
        stmt = (
            select(Lesson)
            .where(
                Lesson.subgroup_id == subgroup_id,
                Lesson.date == lesson_date,
            )
            .order_by(Lesson.start_time)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_for_subgroup_in_range(
        self,
        subgroup_id: int,
        start_date: date,
        end_date: date,
    ) -> Sequence[Lesson]:
        """Find lessons for a subgroup within a date range."""
        stmt = (
            select(Lesson)
            .where(
                and_(
                    Lesson.subgroup_id == subgroup_id,
                    Lesson.date >= start_date,
                    Lesson.date <= end_date,
                )
            )
            .order_by(Lesson.date, Lesson.start_time)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
