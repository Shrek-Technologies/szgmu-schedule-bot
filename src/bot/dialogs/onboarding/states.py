from aiogram.fsm.state import State, StatesGroup


class OnboardingSG(StatesGroup):
    welcome = State()
