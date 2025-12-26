import datetime

from sqlalchemy import BigInteger, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .enums import LessonType


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    subgroup_id: Mapped[int] = mapped_column(
        ForeignKey("subgroups.id", ondelete="CASCADE"), index=False
    )

    subject: Mapped[str] = mapped_column(String(255))
    lesson_type: Mapped[LessonType] = mapped_column()

    date: Mapped[datetime.date] = mapped_column(index=False)
    start_time: Mapped[datetime.time] = mapped_column()
    end_time: Mapped[datetime.time] = mapped_column()

    teacher: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(255))
    room: Mapped[str | None] = mapped_column(String(100))

    __table_args__ = (
        Index("idx_lessons_lookup", "subgroup_id", "date"),
        UniqueConstraint("subgroup_id", "date", "start_time", "subject", name="uq_lesson_unique"),
    )
