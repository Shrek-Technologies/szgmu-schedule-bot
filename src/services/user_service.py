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
    ):
        """Initialize UserService with repositories.

        Args:
            session: AsyncSession for database operations
            user_repo: Repository for users
        """
        self.session = session
        self.user_repo = user_repo

    async def get_or_create_user(self, telegram_id: int, username: str, full_name: str) -> User:
        """Get existing user or create new one.

        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            full_name: User's full name

        Returns:
            User instance
        """
        try:
            user = await self.user_repo.upsert(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
            )
            await self.session.commit()
            logger.info(f"User {telegram_id} created or updated")
            return user

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating/updating user {telegram_id}: {str(e)}")
            raise UserNotFoundError(f"Failed to create/update user: {str(e)}") from e

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
            logger.info(f"User {telegram_id} assigned to subgroup {subgroup_id}")
            return is_updated

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error setting subgroup for user {telegram_id}: {str(e)}")
            raise UserNotFoundError(f"Failed to set subgroup: {str(e)}") from e
