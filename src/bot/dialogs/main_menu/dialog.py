from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Group, Start
from aiogram_dialog.widgets.text import Const
from magic_filter import F

from bot.dialogs.admin.states import AdminSG
from bot.dialogs.group_selection.states import GroupSelectionSG
from bot.dialogs.schedule.states import ScheduleSG
from bot.dialogs.settings.states import SettingsSG

from .getters import get_main_menu_data
from .states import MainMenuSG

dialog = Dialog(
    Window(
        Const("📋 <b>Главное меню</b>"),
        Const("\n\n👥 Группа не выбрана", when=~F["has_group"]),
        Group(
            Start(Const("📅 Расписание"), id="schedule", state=ScheduleSG.view),
            Start(Const("👥 Выбрать группу"), id="group", state=GroupSelectionSG.speciality),
            Start(Const("⚙️ Настройки"), id="settings", state=SettingsSG.view),
            Start(Const("🛠 Админ-панель"), id="admin", state=AdminSG.menu, when="is_admin"),
            width=1,
        ),
        state=MainMenuSG.menu,
        getter=get_main_menu_data,
    ),
    launch_mode=LaunchMode.ROOT,
)
