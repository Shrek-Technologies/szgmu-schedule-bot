from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from services.sync_service import SyncService


@inject
async def on_sync_all(
    callback: CallbackQuery,
    _widget: Button,
    _manager: DialogManager,
    sync_service: FromDishka[SyncService],
) -> None:
    await callback.bot.send_message(
        callback.from_user.id,
        "⏳ Начинается синхронизация расписаний...",
    )

    try:
        await sync_service.sync_all_schedules()
        await callback.bot.send_message(
            callback.from_user.id,
            "✅ Синхронизация завершена успешно",
        )
    except Exception as e:
        await callback.bot.send_message(
            callback.from_user.id,
            f"❌ Ошибка при синхронизации: {str(e)}",
        )
