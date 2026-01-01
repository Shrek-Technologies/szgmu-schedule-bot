from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Back, Cancel, Column, Select, Start
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.main_menu.states import MainMenuSG

from .callbacks import (
    on_course_selected,
    on_group_selected,
    on_speciality_selected,
    on_stream_selected,
    on_subgroup_selected,
)
from .getters import get_courses, get_groups, get_specialities, get_streams, get_subgroups
from .states import GroupSelectionSG

dialog = Dialog(
    Window(
        Const("Выберите специальность:"),
        Column(
            Select(
                Format("{item[1]}"),
                id="spec_select",
                items="items",
                item_id_getter=lambda x: str(x[0]),
                on_click=on_speciality_selected,
            ),
        ),
        Cancel(Const("❌ Отмена")),
        state=GroupSelectionSG.speciality,
        getter=get_specialities,
    ),
    Window(
        Const("Выберите курс:"),
        Column(
            Select(
                Format("{item[1]}"),
                id="course_select",
                items="items",
                item_id_getter=lambda x: str(x[0]),
                on_click=on_course_selected,
            ),
        ),
        Back(Const("← Назад")),
        state=GroupSelectionSG.course,
        getter=get_courses,
    ),
    Window(
        Const("Выберите поток:"),
        Column(
            Select(
                Format("{item[1]}"),
                id="stream_select",
                items="items",
                item_id_getter=lambda x: x[0],
                on_click=on_stream_selected,
            ),
        ),
        Back(Const("← Назад")),
        state=GroupSelectionSG.stream,
        getter=get_streams,
    ),
    Window(
        Const("Выберите группу:"),
        Column(
            Select(
                Format("{item[1]}"),
                id="group_select",
                items="items",
                item_id_getter=lambda x: str(x[0]),
                on_click=on_group_selected,
            ),
        ),
        Back(Const("← Назад")),
        state=GroupSelectionSG.group,
        getter=get_groups,
    ),
    Window(
        Const("Выберите подгруппу:"),
        Column(
            Select(
                Format("{item[1]}"),
                id="subgroup_select",
                items="items",
                item_id_getter=lambda x: str(x[0]),
                on_click=on_subgroup_selected,
            ),
        ),
        Back(Const("← Назад")),
        state=GroupSelectionSG.subgroup,
        getter=get_subgroups,
    ),
    Window(
        Const("✅ <b>Группа успешно выбрана!</b>"),
        Start(Const("⬅️ Вернуться в меню"), id="to_main_menu", state=MainMenuSG.menu),
        state=GroupSelectionSG.success,
    ),
)
