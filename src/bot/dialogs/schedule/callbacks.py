from datetime import date, timedelta

from aiogram.types import CallbackQuery
from aiogram_dialog import ChatEvent, DialogManager
from aiogram_dialog.widgets.kbd import Button, ManagedCheckbox


async def on_mode_changed(
    _event: ChatEvent,
    checkbox: ManagedCheckbox,
    manager: DialogManager,
) -> None:
    manager.dialog_data["mode"] = "week" if checkbox.is_checked() else "day"


async def on_prev(
    _callback: CallbackQuery,
    _widget: Button,
    manager: DialogManager,
) -> None:
    """Navigate to previous day or week based on mode."""
    mode = manager.dialog_data.get("mode", "day")
    anchor_str = manager.dialog_data.get("anchor_date", date.today().isoformat())
    anchor = date.fromisoformat(anchor_str)

    delta = timedelta(days=1) if mode == "day" else timedelta(weeks=1)
    new_anchor = anchor - delta

    manager.dialog_data["anchor_date"] = new_anchor.isoformat()


async def on_next(
    _callback: CallbackQuery,
    _widget: Button,
    manager: DialogManager,
) -> None:
    """Navigate to next day or week based on mode."""
    mode = manager.dialog_data.get("mode", "day")
    anchor_str = manager.dialog_data.get("anchor_date", date.today().isoformat())
    anchor = date.fromisoformat(anchor_str)

    delta = timedelta(days=1) if mode == "day" else timedelta(weeks=1)
    new_anchor = anchor + delta

    manager.dialog_data["anchor_date"] = new_anchor.isoformat()
