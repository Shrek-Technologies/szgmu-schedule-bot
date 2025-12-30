from collections.abc import Sequence
from datetime import time

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from models.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for user operations."""

    async def upsert(
        self,
        telegram_id: int,
        username: str | None,
        full_name: str,
        is_subscribed: bool = False,
        notification_time: time = time(7, 0),
        subgroup_id: int | None = None,
    ) -> User:
        """Upsert user by Telegram ID."""
        stmt = (
            insert(User)
            .values(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
                is_subscribed=is_subscribed,
                notification_time=notification_time,
                subgroup_id=subgroup_id,
            )
            .on_conflict_do_update(
                constraint="users_pkey",
                set_={
                    "username": username,
                    "full_name": full_name,
                },
            )
            .returning(User)
        )

        result = await self.session.execute(stmt)
        user = result.scalar_one()

        await self.session.refresh(user)
        return user

    async def find_by_id(self, telegram_id: int) -> User | None:
        """Find user by Telegram ID."""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_subscription(
        self,
        telegram_id: int,
        is_subscribed: bool,
    ) -> bool:
        """Update user's subscription status. Returns success flag."""
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(is_subscribed=is_subscribed)
            .returning(User.telegram_id)
        )

        result = await self.session.execute(stmt)
        return bool(result.scalar_one_or_none())

    async def update_notification_time(
        self,
        telegram_id: int,
        notification_time: time,
    ) -> bool:
        """Update user's notification time. Returns success flag."""
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(notification_time=notification_time)
            .returning(User.telegram_id)
        )

        result = await self.session.execute(stmt)
        return bool(result.scalar_one_or_none())

    async def update_subgroup(
        self,
        telegram_id: int,
        subgroup_id: int | None,
    ) -> bool:
        """Update user's subgroup. Return success flag."""
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(subgroup_id=subgroup_id)
            .returning(User.telegram_id)
        )

        result = await self.session.execute(stmt)
        return bool(result.scalar_one_or_none())

    async def find_subscribed_users_by_time(self, target_time: time) -> Sequence[User]:
        """Find all users with active subscriptions for a specific time."""
        stmt = (
            select(User)
            .where(
                User.is_subscribed,
                User.subgroup_id.is_not(None),
                User.notification_time == target_time,
            )
            .order_by(User.telegram_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_subscribed_users(self) -> Sequence[User]:
        """Find all users with active subscriptions."""
        stmt = (
            select(User)
            .where(
                User.is_subscribed,
                User.subgroup_id.is_not(None),
            )
            .order_by(User.telegram_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
