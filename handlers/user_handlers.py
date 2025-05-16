import dateparser

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards.keyboards import create_inline_kb, get_note_keyboard
from services.services import FSMContextClass, get_note_text
from data.database import Database
from notification.notification import schedule_notification


router = Router()
db_manager = Database()
scheduler = AsyncIOScheduler()


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
        return

    await message.answer(text='<b>Выбери нужное действие</b>',
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

    max_future = datetime.now(parsed_date.tzinfo) + timedelta(days=365 * 100)
    if parsed_date > max_future:
        await message.answer("❌ Слишком далёкая дата. Укажите дату в ближайших годах.")
        return

    data = await state.get_data()
    title = data['fill_title']
    text = data.get('fill_text', '')

    note = db_manager.create_note(
        user_id=message.from_user.id,
        data_start=datetime.now(),
        data_end=parsed_date,
        note_text=text,
        note_title=title
    )

    schedule_notification(note_id=note.note_id, deadline_end=parsed_date)

    await state.clear()

    await message.answer(f"✅ Дедлайн <b>{title}</b> создан на {parsed_date.strftime('%d.%m.%Y %H:%M')}")
    await message.answer(text='<b>Выбери нужное действие</b>',
                         reply_markup=create_inline_kb(width=1, dct={'add_new_note': 'Добавить новый дедлайн',
                                                                     'my_notes': 'Просмотр дедлайнов'}))


@router.message(StateFilter(FSMContextClass.edit_title))
async def edit_title(message: Message,
                     state: FSMContext):
    title = message.text.strip()

    if len(title) < 2:
        await message.answer("❌ Название слишком короткое. Минимум 2 символа.")
        return
    elif len(title) > 30:
        await message.answer("❌ Название слишком длинное. Максимум 30 символов.")
        return
    data = await state.get_data()
    db_manager.update_note_title(note_id=data['note_id'], new_title=title)
    await state.set_state(FSMContextClass.edit_text)
    await message.answer("Введите текст дедлайна (до 200 символов):")


@router.message(StateFilter(FSMContextClass.edit_text))
async def edit_text(message: Message,
                    state: FSMContext):
    text = message.text.strip()

    if len(text) > 200:
        await message.answer("❌ Текст не должен превышать 200 символов.")
        return

    data = await state.get_data()

    db_manager.update_note_text(note_id=data['note_id'], new_text=text)

    note = db_manager.get_note(note_id=data['note_id'])

    note_text = get_note_text(note)

    reply_markup = get_note_keyboard(data['note_id'])

    await state.clear()

    await message.answer(text=note_text, reply_markup=reply_markup)


@router.message(StateFilter(FSMContextClass.extend_deadline))
async def extend_deadline(message: Message,
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
    db_manager.update_note_deadline(note_id=data['note_id'], new_data_end=parsed_date)

    note = db_manager.get_note(note_id=data['note_id'])

    note_text = get_note_text(note)

    reply_markup = get_note_keyboard(data['note_id'])

    schedule_notification(note_id=note.note_id, deadline_end=parsed_date)

    await state.clear()
    await message.answer(text=note_text, reply_markup=reply_markup)
