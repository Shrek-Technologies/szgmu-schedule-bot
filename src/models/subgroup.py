from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .group import Group


class Subgroup(Base):
    __tablename__ = "subgroups"

    id: Mapped[int] = mapped_column(primary_key=True)

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(20))

    group: Mapped["Group"] = relationship(back_populates="subgroups")

    __table_args__ = (UniqueConstraint("group_id", "name", name="uq_subgroups_group_name"),)
