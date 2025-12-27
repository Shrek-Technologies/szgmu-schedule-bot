from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .speciality import Speciality
    from .subgroup import Subgroup


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)

    speciality_id: Mapped[int] = mapped_column(ForeignKey("specialities.id", ondelete="CASCADE"))
    course_number: Mapped[int] = mapped_column(SmallInteger)
    stream: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(20))

    speciality: Mapped["Speciality"] = relationship(back_populates="groups")

    subgroups: Mapped[list["Subgroup"]] = relationship(
        back_populates="group", lazy="selectin", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_groups_structure", "speciality_id", "course_number", "stream"),
        UniqueConstraint(
            "speciality_id", "course_number", "stream", "name", name="uq_groups_identity"
        ),
    )
