from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Cancel, Checkbox
from aiogram_dialog.widgets.text import Const, Format

from .callbacks import on_toggle_notifications
from .getters import get_user_settings
from .states import SettingsSG

dialog = Dialog(
    Window(
        Format("{settings_text}"),
        Checkbox(
            Const("🔔 Включить уведомления"),
            Const("🔕 Отключить уведомления"),
            id="notifications",
            on_state_changed=on_toggle_notifications,
        ),
        Cancel(Const("← Назад")),
        state=SettingsSG.view,
        getter=get_user_settings,
    ),
)
