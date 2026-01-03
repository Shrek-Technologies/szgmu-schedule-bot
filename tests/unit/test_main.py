"""Unit tests for main module functions."""

from unittest.mock import MagicMock, patch

from aiogram.fsm.storage.memory import MemoryStorage

from src.core.config import RedisSettings
from src.main import create_storage


class TestCreateStorage:
    """Tests for create_storage function."""

    def test_create_storage_memory_storage_default(self) -> None:
        """Test create_storage returns MemoryStorage by default."""
        storage = create_storage(use_redis=False)
        assert isinstance(storage, MemoryStorage)

    def test_create_storage_memory_storage_when_use_redis_false(self) -> None:
        """Test create_storage returns MemoryStorage when use_redis=False."""
        storage = create_storage(use_redis=False, redis_settings=None)
        assert isinstance(storage, MemoryStorage)

    def test_create_storage_with_none_redis_settings(self) -> None:
        """Test create_storage uses MemoryStorage when redis_settings is None."""
        storage = create_storage(use_redis=True, redis_settings=None)
        assert isinstance(storage, MemoryStorage)

    def test_create_storage_redis_settings_provided_false(self) -> None:
        """Test create_storage ignores redis_settings when use_redis=False."""
        redis_settings = MagicMock(spec=RedisSettings)
        storage = create_storage(use_redis=False, redis_settings=redis_settings)
        assert isinstance(storage, MemoryStorage)

    @patch("src.main.RedisStorage")
    def test_create_storage_redis_connection_error_fallback(self, mock_redis_storage_class):  # type: ignore[no-untyped-def]
        """Test create_storage falls back to MemoryStorage on Redis connection error."""
        mock_redis_storage_class.from_url.side_effect = ConnectionError("Connection failed")
        redis_settings = MagicMock(spec=RedisSettings)
        redis_settings.dsn = "redis://localhost:6379/0"

        storage = create_storage(use_redis=True, redis_settings=redis_settings)

        assert isinstance(storage, MemoryStorage)

    @patch("src.main.RedisStorage")
    def test_create_storage_redis_runtime_error_fallback(self, mock_redis_storage_class):  # type: ignore[no-untyped-def]
        """Test create_storage falls back to MemoryStorage on Redis RuntimeError."""
        mock_redis_storage_class.from_url.side_effect = RuntimeError("Redis error")
        redis_settings = MagicMock(spec=RedisSettings)
        redis_settings.dsn = "redis://localhost:6379/0"

        storage = create_storage(use_redis=True, redis_settings=redis_settings)

        assert isinstance(storage, MemoryStorage)
