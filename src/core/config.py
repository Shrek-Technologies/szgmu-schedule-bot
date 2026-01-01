from pathlib import Path

from pydantic import (
    Field,
    HttpUrl,
    PositiveInt,
    SecretStr,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class BotSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="BOT_")

    token: SecretStr = Field(..., description="Telegram Bot Token")
    admin_ids: list[int] = Field(default_factory=list, description="List of admin Telegram IDs")
    use_redis: bool = Field(default=False, description="Use RedisStorage vs MemoryStorage")


class DatabaseSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str = Field(default="localhost", description="DB host")
    port: int = Field(default=5432, description="DB port")
    user: str = Field(..., description="DB user")
    password: SecretStr = Field(..., description="DB password")
    database: str = Field(..., description="DB name")

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+psycopg://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class RedisSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    password: SecretStr = Field(..., description="DB password")
    database: int = Field(default=0, description="Redis database")

    @property
    def dsn(self) -> str:
        if self.password:
            return f"redis://{self.password.get_secret_value()}@{self.host}:{self.port}/{self.database}"
        return f"redis://{self.host}:{self.port}/{self.database}"


class APISettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="API_")

    schedule_url: HttpUrl = Field(..., description="University schedule API")
    timeout_seconds: PositiveInt = Field(default=30)


class AppSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="APP_")

    cache_ttl_seconds: PositiveInt = Field(default=3600)
    log_level: str = Field(default="INFO")


class Settings(ConfigBase):
    bot: BotSettings = Field(default_factory=BotSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    api: APISettings = Field(default_factory=APISettings)
    app: AppSettings = Field(default_factory=AppSettings)
