from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider

from .providers.api_client import ApiProvider
from .providers.config import ConfigProvider
from .providers.database import DatabaseProvider
from .providers.repositories import RepositoryProvider
from .providers.services import ServiceProvider


def create_container():
    """Create and configure Dishka container."""
    return make_async_container(
        ConfigProvider(),
        DatabaseProvider(),
        ApiProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        AiogramProvider(),
    )
