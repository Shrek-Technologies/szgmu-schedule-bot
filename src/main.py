import asyncio
import logging
import sys

# from aiogram import Bot, Dispatcher
# from dishka.integrations.aiogram import setup_dishka
from di.container import create_container
from services.sync_service import SyncService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Main application."""
    logger.info("Starting initial sync...")

    # settings = Settings()

    # bot = Bot(settings.bot.token.get_secret_value())
    # dp = Dispatcher()

    container = create_container()
    # setup_dishka(container, router=dp, auto_inject=True)

    try:
        async with container() as nested_container:
            sync_service = await nested_container.get(SyncService)
            await run_initial_sync(sync_service)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await container.close()
        # await bot.session.close()
        logger.info("Stopped")


async def run_initial_sync(sync_service: SyncService):
    """Run initial sync on startup."""
    logger.info("Running initial sync...")

    try:
        await sync_service.sync_all_schedules()
        logger.info("Initial sync completed")

    except Exception as e:
        logger.error(f"Initial sync failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Fix for Windows + psycopg async
    if sys.platform == "win32":
        asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
    else:
        asyncio.run(main())
