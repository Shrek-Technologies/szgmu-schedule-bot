import logging

from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from repositories.user_repo import UserRepository
from .exceptions import UserNotFoundError

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user profiles."""

    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
    ) -> None:
        """Initialize UserService with repositories.

        Args:
            session: AsyncSession for database operations
            user_repo: Repository for users
        """
        self.session = session
        self.user_repo = user_repo

    async def get_or_create_user(
        self, telegram_id: int, username: str | None, full_name: str
    ) -> User:
        """Get existing user or create new one.

        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            full_name: User's full name

        Returns:
            User instance
        """
        user = await self.user_repo.upsert(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
        )
        await self.session.commit()
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID.

        Args:
            telegram_id: Telegram user ID

        Returns:
            User instance or None if not found
        """
        return await self.user_repo.find_by_id(telegram_id)

    async def set_user_subgroup(self, telegram_id: int, subgroup_id: int) -> bool:
        """Set user's subgroup.

        Args:
            telegram_id: Telegram user ID
            subgroup_id: ID of the subgroup to assign

        Returns:
            True if user was updated, False otherwise

        Raises:
            UserNotFoundError: If user not found
        """
        try:
            is_updated = await self.user_repo.update_subgroup(telegram_id, subgroup_id)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error("Error setting subgroup for user %d: %s", telegram_id, e)
            raise UserNotFoundError(f"Failed to set subgroup: {e!s}") from e
        logger.info("User %d assigned to subgroup %d", telegram_id, subgroup_id)
        return is_updated
