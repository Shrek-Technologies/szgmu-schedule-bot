from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Group, Start
from aiogram_dialog.widgets.text import Const

from bot.dialogs.group_selection.states import GroupSelectionSG
from bot.dialogs.main_menu.states import MainMenuSG

from .states import OnboardingSG

dialog = Dialog(
    Window(
        Const(
            "👋 Добро пожаловать!\n\n"
            "Этот бот помогает просматривать расписание занятий.\n\n"
            "Начнем с выбора группы?"
        ),
        Group(
            Start(
                Const("📚 Выбрать группу"),
                id="start_group",
                state=GroupSelectionSG.speciality,
            ),
            Start(
                Const("↩️ Позже"),
                id="skip",
                state=MainMenuSG.menu,
            ),
            width=1,
        ),
        state=OnboardingSG.welcome,
    ),
)
