"""Unit tests for core configuration."""

from pydantic import SecretStr

from src.core.config import (
    APISettings,
    AppSettings,
    BotSettings,
    DatabaseSettings,
    RedisSettings,
)


class TestBotSettings:
    """Tests for BotSettings."""

    def test_bot_settings_initialization(self) -> None:
        """Test BotSettings initialization."""
        settings = BotSettings.model_construct(
            token=SecretStr("test-token"), admin_ids=[123], use_redis=False
        )
        assert isinstance(settings.token, SecretStr)
        assert settings.admin_ids == [123]
        assert settings.use_redis is False

    def test_bot_settings_default_use_redis(self) -> None:
        """Test BotSettings default use_redis is False."""
        settings = BotSettings.model_construct(token="test-token", admin_ids=[], use_redis=False)
        assert settings.use_redis is False

    def test_bot_settings_empty_admin_ids(self) -> None:
        """Test BotSettings with empty admin_ids."""
        settings = BotSettings.model_construct(token="test-token", admin_ids=[])
        assert settings.admin_ids == []

    def test_bot_settings_multiple_admin_ids(self) -> None:
        """Test BotSettings with multiple admin IDs."""
        settings = BotSettings.model_construct(token="test-token", admin_ids=[123, 456, 789])
        assert len(settings.admin_ids) == 3


class TestDatabaseSettings:
    """Tests for DatabaseSettings."""

    def test_database_settings_initialization(self) -> None:
        """Test DatabaseSettings initialization."""
        settings = DatabaseSettings.model_validate(
            {"user": "testuser", "password": "testpass", "database": "testdb"}
        )
        assert settings.user == "testuser"
        assert settings.password.get_secret_value() == "testpass"
        assert settings.database == "testdb"

    def test_database_settings_default_host(self) -> None:
        """Test DatabaseSettings default host."""
        settings = DatabaseSettings.model_validate(
            {"user": "testuser", "password": "testpass", "database": "testdb"}
        )
        assert settings.host == "localhost"

    def test_database_settings_default_port(self) -> None:
        """Test DatabaseSettings default port."""
        settings = DatabaseSettings.model_validate(
            {"user": "testuser", "password": "testpass", "database": "testdb"}
        )
        assert settings.port == 5432

    def test_database_settings_dsn_property(self) -> None:
        """Test DatabaseSettings dsn property."""
        settings = DatabaseSettings.model_validate(
            {
                "user": "testuser",
                "password": "testpass",
                "database": "testdb",
                "host": "db.example.com",
                "port": 5433,
            }
        )
        dsn = settings.dsn
        assert "testuser" in dsn
        assert "testpass" in dsn
        assert "db.example.com" in dsn
        assert "5433" in dsn
        assert "testdb" in dsn
        assert "postgresql+psycopg" in dsn


class TestRedisSettings:
    """Tests for RedisSettings."""

    def test_redis_settings_initialization(self) -> None:
        """Test RedisSettings initialization."""
        settings = RedisSettings.model_validate({"password": "redispass"})
        assert settings.password.get_secret_value() == "redispass"

    def test_redis_settings_default_host(self) -> None:
        """Test RedisSettings default host."""
        settings = RedisSettings.model_validate({"password": "redispass"})
        assert settings.host == "localhost"

    def test_redis_settings_default_port(self) -> None:
        """Test RedisSettings default port."""
        settings = RedisSettings.model_validate({"password": "redispass"})
        assert settings.port == 6379

    def test_redis_settings_default_database(self) -> None:
        """Test RedisSettings default database."""
        settings = RedisSettings.model_validate({"password": "redispass"})
        assert settings.database == 0

    def test_redis_settings_dsn_property(self) -> None:
        """Test RedisSettings dsn property."""
        settings = RedisSettings.model_validate(
            {
                "password": "redispass",
                "host": "redis.example.com",
                "port": 6380,
                "database": 1,
            }
        )
        dsn = settings.dsn
        assert "redis://" in dsn
        assert "redispass" in dsn
        assert "redis.example.com" in dsn
        assert "6380" in dsn
        assert "1" in dsn


class TestAPISettings:
    """Tests for APISettings."""

    def test_api_settings_initialization(self) -> None:
        """Test APISettings initialization."""
        settings = APISettings.model_validate({"schedule_url": "https://api.example.com"})
        assert str(settings.schedule_url) == "https://api.example.com/"

    def test_api_settings_default_timeout(self) -> None:
        """Test APISettings default timeout."""
        settings = APISettings.model_validate({"schedule_url": "https://api.example.com"})
        assert settings.timeout_seconds == 30

    def test_api_settings_custom_timeout(self) -> None:
        """Test APISettings with custom timeout."""
        settings = APISettings.model_validate(
            {"schedule_url": "https://api.example.com", "timeout_seconds": 60}
        )
        assert settings.timeout_seconds == 60


class TestAppSettings:
    """Tests for AppSettings."""

    def test_app_settings_initialization(self) -> None:
        """Test AppSettings initialization."""
        settings = AppSettings.model_validate({})
        assert settings.cache_ttl_seconds == 3600
        assert settings.log_level == "INFO"

    def test_app_settings_custom_values(self) -> None:
        """Test AppSettings with custom values."""
        settings = AppSettings.model_validate({"cache_ttl_seconds": 7200, "log_level": "DEBUG"})
        assert settings.cache_ttl_seconds == 7200
        assert settings.log_level == "DEBUG"
