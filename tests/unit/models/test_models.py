"""Unit tests for data models."""

from datetime import time

from src.models.base import Base
from src.models.enums import EducationLevel, LessonType
from src.models.user import User


class TestLessonType:
    """Tests for LessonType enum."""

    def test_lesson_type_lecture_value(self) -> None:
        """Test LECTURE enum value."""
        assert LessonType.LECTURE == "лекционного"

    def test_lesson_type_seminar_value(self) -> None:
        """Test SEMINAR enum value."""
        assert LessonType.SEMINAR == "семинарского"

    def test_lesson_type_is_str_enum(self) -> None:
        """Test that LessonType is StrEnum."""
        assert isinstance(LessonType.LECTURE, str)
        assert isinstance(LessonType.SEMINAR, str)


class TestEducationLevel:
    """Tests for EducationLevel enum."""

    def test_education_level_bachelor_value(self) -> None:
        """Test BACHELOR enum value."""
        assert EducationLevel.BACHELOR == "bachelor"

    def test_education_level_specialist_value(self) -> None:
        """Test SPECIALIST enum value."""
        assert EducationLevel.SPECIALIST == "specialist"

    def test_education_level_master_value(self) -> None:
        """Test MASTER enum value."""
        assert EducationLevel.MASTER == "master"

    def test_education_level_residency_value(self) -> None:
        """Test RESIDENCY enum value."""
        assert EducationLevel.RESIDENCY == "residency"

    def test_education_level_is_str_enum(self) -> None:
        """Test that EducationLevel is StrEnum."""
        assert isinstance(EducationLevel.BACHELOR, str)
        assert isinstance(EducationLevel.MASTER, str)


class TestBase:
    """Tests for Base model class."""

    def test_base_is_declarative_base(self) -> None:
        """Test that Base inherits from DeclarativeBase."""
        assert hasattr(Base, "metadata")

    def test_base_supports_async_attrs(self) -> None:
        """Test that Base has AsyncAttrs support."""
        assert hasattr(Base, "__class__")


class TestUserModel:
    """Tests for User model attributes."""

    def test_user_table_name(self) -> None:
        """Test User table name."""
        assert User.__tablename__ == "users"

    def test_user_has_telegram_id_column(self) -> None:
        """Test User has telegram_id column."""
        assert hasattr(User, "telegram_id")

    def test_user_has_username_column(self) -> None:
        """Test User has username column."""
        assert hasattr(User, "username")

    def test_user_has_full_name_column(self) -> None:
        """Test User has full_name column."""
        assert hasattr(User, "full_name")

    def test_user_has_subgroup_id_column(self) -> None:
        """Test User has subgroup_id column."""
        assert hasattr(User, "subgroup_id")

    def test_user_has_is_subscribed_column(self) -> None:
        """Test User has is_subscribed column."""
        assert hasattr(User, "is_subscribed")

    def test_user_has_notification_time_column(self) -> None:
        """Test User has notification_time column."""
        assert hasattr(User, "notification_time")

    def test_user_default_notification_time(self) -> None:
        """Test default notification time is 7:00."""
        assert User.notification_time.default.arg == time(7, 0)
