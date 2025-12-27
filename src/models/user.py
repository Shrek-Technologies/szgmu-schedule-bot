from datetime import time

from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .subgroup import Subgroup


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)

    username: Mapped[str | None] = mapped_column(String(32))
    full_name: Mapped[str] = mapped_column(String(100))

    subgroup_id: Mapped[int | None] = mapped_column(ForeignKey("subgroups.id", ondelete="SET NULL"))

    # Subscription Config
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_time: Mapped[time] = mapped_column(default=time(7, 0))  # 7:00 AM default

    subgroup: Mapped["Subgroup"] = relationship()
