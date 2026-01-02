from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Start
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.main_menu.states import MainMenuSG
from .callbacks import on_sync_all
from .states import AdminSG

dialog = Dialog(
    Window(
        Const("⚙️ <b>Панель администратора</b>"),
        Button(Const("🔄 Принудительная синхронизация"), id="sync", on_click=on_sync_all),
        Cancel(Const("← Назад")),
        state=AdminSG.menu,
    ),
    Window(
        Const("🔄 <b>Синхронизация запущена</b>\n\nПожалуйста, подождите…"),
        state=AdminSG.syncing,
    ),
    Window(
        Const("✅ <b>Синхронизация завершена</b>"),
        Start(Const("⬅️ Вернуться в меню"), id="to_main_menu", state=MainMenuSG.menu),
        state=AdminSG.done,
    ),
    Window(
        Format("❌ <b>Ошибка</b>\n\n{error}"),
        Start(Const("⬅️ Вернуться в меню"), id="to_main_menu", state=MainMenuSG.menu),
        state=AdminSG.error,
    ),
)
