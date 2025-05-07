from aiogram import Bot
from aiogram.types import BotCommand

from keyboards.keyboards import PointsCallbackFactory
from aiogram.fsm.state import State, StatesGroup


class FSMContextClass(StatesGroup):
    menu_context = State()
    fill_title = State()
    fill_text = State()
    fill_deadline = State()
    note_selection = State()
    note_viewing = State()
    note_edit = State()
