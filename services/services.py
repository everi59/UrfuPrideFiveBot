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


# Константы для хранения состояний
MENU_MAIN = "main"
MENU_CREATE = "create"
MENU_VIEW = "view"
MENU_EDIT = "edit"


def create_text_of_notes(notes, page=0):
    result = "📌 <b>Ваши дедлайны:</b>\n\n"
    notes = notes[page*4:min(len(notes), page*4+4)]
    for note in notes:
        deadline_str = note.data_end.strftime("%d.%m.%Y %H:%M")
        title = note.note_title
        text = note.note_text if note.note_text else "<без описания>"
        result += f"📘 <b>{title}</b>\n{text[:50]}{'...' if len(text) > 50 else ''}\n📅 До: {deadline_str}\n\n"

    return result
