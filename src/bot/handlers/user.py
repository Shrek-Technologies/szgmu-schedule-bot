from aiogram import Router
from aiogram.filters import Command, ExceptionTypeFilter
from aiogram.types import Message
from aiogram_dialog import ChatEvent, DialogManager, ShowMode, StartMode
from aiogram_dialog.api.exceptions import UnknownIntent
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from bot.dialogs.main_menu.states import MainMenuSG
from bot.dialogs.onboarding.states import OnboardingSG
from services.user_service import UserService

router = Router()


@router.message(Command("start"))
@inject
async def start_command(
    message: Message,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
) -> None:
    user = await user_service.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )

    if user and user.subgroup_id:
        await dialog_manager.start(MainMenuSG.menu)
    else:
        await dialog_manager.start(OnboardingSG.welcome)


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    help_text = (
        "📚 <b>Справка по боту</b>\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать справку\n"
        "В главном меню доступны:\n"
        "📅 <b>Расписание</b> - Просмотр расписания\n"
        "👥 <b>Выбрать группу</b> - Изменить группу\n"
        "⚙️ <b>Настройки</b> - Настройки уведомлений"
    )
    await message.answer(help_text)


@router.message()
async def default_handler(message: Message) -> None:
    await message.answer(
        "❓ Команда не понята. Используйте /help для справки или /start для главного меню."
    )


@router.errors(ExceptionTypeFilter(UnknownIntent))
async def on_unknown_intent(_event: ChatEvent, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(
        MainMenuSG.menu,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )
