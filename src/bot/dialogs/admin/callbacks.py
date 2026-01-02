from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from services.sync_service import SyncService
from .states import AdminSG


@inject
async def on_sync_all(
    _callback: CallbackQuery,
    _widget: Button,
    manager: DialogManager,
    sync_service: FromDishka[SyncService],
) -> None:
    await manager.switch_to(AdminSG.syncing)
    await manager.show()

    try:
        await sync_service.sync_all_schedules()
        await manager.switch_to(AdminSG.done)

    except Exception as e:
        manager.dialog_data["error"] = str(e)
        await manager.switch_to(AdminSG.error)
