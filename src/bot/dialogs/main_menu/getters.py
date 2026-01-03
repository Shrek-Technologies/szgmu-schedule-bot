from typing import Any

from aiogram.types import User
from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

import models
from core.config import BotSettings
from services.user_service import UserService


@inject
async def get_main_menu_data(
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    settings: FromDishka[BotSettings],
    **_: object,
) -> dict[str, Any]:
    tg_user: User = dialog_manager.middleware_data["event_from_user"]
    user: models.User = await user_service.get_or_create_user(
        tg_user.id, tg_user.username, tg_user.full_name
    )

    return {
        "has_group": user.subgroup_id is not None,
        "is_admin": user.telegram_id in settings.admin_ids,
    }
