from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from api.client import ScheduleAPIClient
from core.config import APISettings


class ApiProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_api_client(
        self,
        api_settings: APISettings,
    ) -> AsyncIterator[ScheduleAPIClient]:
        client = ScheduleAPIClient(
            base_url=str(api_settings.schedule_url),
            timeout=api_settings.timeout_seconds,
        )
        yield client
        await client.close()
