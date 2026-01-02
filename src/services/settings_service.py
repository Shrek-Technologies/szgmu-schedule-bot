import logging
from collections.abc import Sequence
from datetime import time

from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)


class SettingsService:
    """Service for managing user notification settings."""

    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
    ) -> None:
        """Initialize SettingsService with repository.

        Args:
            session: AsyncSession for database operations
            user_repo: Repository for users
        """
        self.session = session
        self.user_repo = user_repo

    async def toggle_notifications(self, telegram_id: int, is_subscribed: bool) -> bool:
        """Toggle notifications on or off for a user.

        Args:
            telegram_id: Telegram user ID
            is_subscribed: Whether notifications should be enabled

        Returns:
            True if user was updated, False otherwise
        """
        is_updated = await self.user_repo.update_subscription(telegram_id, is_subscribed)
        await self.session.commit()
        logger.info("User %d notifications toggled: %s", telegram_id, is_subscribed)
        return is_updated

    async def set_notification_time(self, telegram_id: int, notification_time: time) -> bool:
        """Set notification time for a user.

        Args:
            telegram_id: Telegram user ID
            notification_time: Time in datetime.time format

        Returns:
            True if user was updated, False otherwise
        """
        is_updated = await self.user_repo.update_notification_time(telegram_id, notification_time)
        await self.session.commit()
        logger.info("User %d notification time set to %s", telegram_id, notification_time)
        return is_updated

    async def get_users_for_notification_batch(self, target_time: time) -> Sequence[User]:
        """Get all subscribed users with a specific notification time.

        Args:
            target_time: Time to match

        Returns:
            List of User objects with matching notification time and subscribed=True
        """
        return await self.user_repo.find_subscribed_users_by_time(target_time)
