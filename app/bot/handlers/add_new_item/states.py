from aiogram.dispatcher.filters.state import State, StatesGroup


class AddNewItemStates(StatesGroup):
    waiting_for_item_name = State()

