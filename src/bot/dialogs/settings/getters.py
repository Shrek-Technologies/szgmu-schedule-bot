from typing import Any

from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from services.user_service import UserService


@inject
async def get_user_settings(
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    **_: object,
) -> dict[str, Any]:
    telegram_id = dialog_manager.middleware_data["event_from_user"].id
    user = await user_service.get_by_telegram_id(telegram_id)

    if not user:
        return {
            "settings_text": "❌ Пользователь не найден",
            "is_subscribed": False,
        }

    subscription_status = "✅ Включены" if user.is_subscribed else "❌ Выключены"
    notification_time = user.notification_time.strftime("%H:%M")

    settings_text = (
        f"⚙️ <b>Настройки</b>\n\n"
        f"🔔 Уведомления: {subscription_status}\n"
        f"⏰ Время уведомлений: {notification_time}"
    )

    return {
        "settings_text": settings_text,
        "is_subscribed": user.is_subscribed,
        "notification_time": notification_time,
    }
