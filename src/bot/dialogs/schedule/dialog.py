from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Checkbox, Group
from aiogram_dialog.widgets.text import Const, Format

from .callbacks import (
    on_mode_changed,
    on_next,
    on_prev,
)
from .getters import get_schedule
from .states import ScheduleSG

dialog = Dialog(
    Window(
        Format("{schedule_text}"),
        Group(
            Button(Const("◀️"), id="prev", on_click=on_prev),
            Button(Const("▶️"), id="next", on_click=on_next),
            width=2,
        ),
        Checkbox(
            Const("📆 Неделя"),
            Const("📅 День"),
            id="mode",
            on_state_changed=on_mode_changed,
        ),
        Cancel(Const("← В меню")),
        state=ScheduleSG.view,
        getter=get_schedule,
    ),
)
