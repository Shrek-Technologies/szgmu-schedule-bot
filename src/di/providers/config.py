from dishka import Provider, Scope, provide

from core.config import (
    APISettings,
    AppSettings,
    BotSettings,
    DatabaseSettings,
    RedisSettings,
    Settings,
)


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_settings(self) -> Settings:
        return Settings()

    @provide(scope=Scope.APP)
    def provide_bot_settings(self, settings: Settings) -> BotSettings:
        return settings.bot

    @provide(scope=Scope.APP)
    def provide_db_settings(self, settings: Settings) -> DatabaseSettings:
        return settings.db

    @provide(scope=Scope.APP)
    def provide_api_settings(self, settings: Settings) -> APISettings:
        return settings.api

    @provide(scope=Scope.APP)
    def provide_app_settings(self, settings: Settings) -> AppSettings:
        return settings.app

    @provide(scope=Scope.APP)
    def provide_redis_settings(self, settings: Settings) -> RedisSettings:
        return settings.redis
