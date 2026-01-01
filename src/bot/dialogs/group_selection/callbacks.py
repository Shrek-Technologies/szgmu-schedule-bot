from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from services.user_service import UserService


async def on_speciality_selected(
    _callback: CallbackQuery,
    _widget: Select,
    manager: DialogManager,
    item_id: str,
) -> None:
    manager.dialog_data["speciality_id"] = int(item_id)
    await manager.next()


async def on_course_selected(
    _callback: CallbackQuery,
    _widget: Select,
    manager: DialogManager,
    item_id: str,
) -> None:
    manager.dialog_data["course"] = int(item_id)
    await manager.next()


async def on_stream_selected(
    _callback: CallbackQuery,
    _widget: Select,
    manager: DialogManager,
    item_id: str,
) -> None:
    manager.dialog_data["stream"] = item_id
    await manager.next()


async def on_group_selected(
    _callback: CallbackQuery,
    _widget: Select,
    manager: DialogManager,
    item_id: str,
) -> None:
    manager.dialog_data["group_id"] = int(item_id)
    await manager.next()


@inject
async def on_subgroup_selected(
    callback: CallbackQuery,
    _widget: Select,
    manager: DialogManager,
    item_id: str,
    user_service: FromDishka[UserService],
) -> None:
    subgroup_id = int(item_id)
    manager.dialog_data["subgroup_id"] = subgroup_id
    telegram_id = callback.from_user.id
    await user_service.set_user_subgroup(telegram_id, subgroup_id)
    await manager.next()
