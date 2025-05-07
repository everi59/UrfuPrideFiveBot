import dateparser

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from datetime import datetime

from keyboards.keyboards import create_inline_kb
from services.services import FSMContextClass
from data.database import Database


router = Router()
db_manager = Database()


# START_COMMAND
@router.message(CommandStart(), StateFilter(default_state))
async def start(message: Message):
    user_id = message.from_user.id
    user_fullname = message.from_user.full_name

    user = db_manager.get_user(user_id)
    if not user:
        db_manager.create_user(user_id=user_id, user_fullname=user_fullname)

    await message.answer(text='Привет! Я помогу тебе следить за дедлайнами и\nдомашними заданиями.\n'
                              '<b>Выбери нужное действие</b>',
                         reply_markup=create_inline_kb(width=1, dct={'add_new_note': 'Добавить новый дедлайн',
                                                                     'my_notes': 'Просмотр дедлайнов'}))


# HELP_COMMAND
@router.message(Command(commands='help'))
async def command_help(message: Message):
    if not user:
        db_manager.create_user(user_id=user_id, user_fullname=user_fullname)
    await message.answer(text='Это бот для удобного хранения дедлайнов.\nЧтобы добавить новый дедлайн или посмотреть '
                              'текущие нажми /start')


@router.message(StateFilter(FSMContextClass.fill_title))
async def fill_title(message: Message,
                     state: FSMContext):
    title = message.text.strip()

    if len(title) < 2:
        await message.answer("❌ Название слишком короткое. Минимум 2 символа.")
        return
    elif len(title) > 30:
        await message.answer("❌ Название слишком длинное. Максимум 30 символов.")
        return

    await state.update_data(fill_title=title)
    await state.set_state(FSMContextClass.fill_text)

    await message.answer("Введите текст дедлайна (до 200 символов):")


@router.message(StateFilter(FSMContextClass.fill_text))
async def fill_text(message: Message,
                    state: FSMContext):
    text = message.text.strip()

    if len(text) > 200:
        await message.answer("❌ Текст не должен превышать 200 символов.")
        return

    await state.update_data(fill_text=text)
    await state.set_state(FSMContextClass.fill_deadline_end)

    await message.answer("Введите дату окончания дедлайна:")


@router.message(StateFilter(FSMContextClass.fill_deadline_end))
async def fill_deadline_end(message: Message,
                            state: FSMContext):
    user_date = message.text.strip()
    parsed_date = dateparser.parse(user_date, languages=['ru'])

    if not parsed_date:
        await message.answer("❌ Не удалось распознать дату. Попробуйте ещё раз.")
        return

    if parsed_date < datetime.now(parsed_date.tzinfo):
        await message.answer("❌ Дата не может быть в прошлом.")
        return

    data = await state.get_data()
    title = data['fill_title']
    text = data.get('fill_text', '')

    db_manager.create_note(
        user_id=message.from_user.id,
        data_start=datetime.now(),
        data_end=parsed_date,
        note_text=text,
        note_title=title
    )

    await message.answer(f"✅ Дедлайн '{title}' создан на {parsed_date.strftime('%d.%m.%Y %H:%M')}")

