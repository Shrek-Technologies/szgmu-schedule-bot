from aiogram.fsm.state import State, StatesGroup


class GroupSelectionSG(StatesGroup):
    """Group selection state group."""

    speciality = State()
    course = State()
    stream = State()
    group = State()
    subgroup = State()
    success = State()
