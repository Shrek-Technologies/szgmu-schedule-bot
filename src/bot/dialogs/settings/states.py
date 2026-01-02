from aiogram.fsm.state import State, StatesGroup


class SettingsSG(StatesGroup):
    view = State()
