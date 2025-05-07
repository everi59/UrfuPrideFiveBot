from aiogram import Bot
from aiogram.types import BotCommand

from aiogram.fsm.state import State, StatesGroup


class FSMContextClass(StatesGroup):
    # Нахождение в главном меню
    menu = State()

    # Создание дедлайна
    fill_title = State()
    fill_text = State()
    fill_deadline_end = State()
