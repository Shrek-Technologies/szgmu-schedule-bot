from aiogram.fsm.state import State, StatesGroup


class AdminSG(StatesGroup):
    menu = State()
    syncing = State()
    done = State()
    error = State()
