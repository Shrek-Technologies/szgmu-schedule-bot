from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import ManagedCheckbox
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from services.settings_service import SettingsService
from services.user_service import UserService


@inject
async def on_toggle_notifications(
    callback: CallbackQuery,
    _checkbox: ManagedCheckbox,
    _manager: DialogManager,
    settings_service: FromDishka[SettingsService],
    user_service: FromDishka[UserService],
) -> None:
    if not callback.from_user:
        return

    user = await user_service.get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name,
    )
    current_state = user.is_subscribed
    await settings_service.toggle_notifications(callback.from_user.id, not current_state)

    await callback.answer("✅ Настройки обновлены")
