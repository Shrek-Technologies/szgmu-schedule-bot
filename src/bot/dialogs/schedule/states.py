from aiogram.fsm.state import State, StatesGroup


class ScheduleSG(StatesGroup):
    view = State()
