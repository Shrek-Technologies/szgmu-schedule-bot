from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from core.config import BotSettings
from services.user_service import UserService


@inject
async def get_main_menu_data(
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    settings: FromDishka[BotSettings],
    **_: object,
) -> dict:
    telegram_id = dialog_manager.middleware_data["event_from_user"].id
    user = await user_service.get_by_telegram_id(telegram_id)
    if not user or not user.subgroup_id:
        return {"has_group": False}

    return {
        "has_group": True,
        "is_admin": telegram_id in settings.admin_ids,
    }
