from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config.config import Config, load_config
from services.services import FSMContextClass, create_text_of_notes
from data.database import Database
from keyboards.keyboards import get_pagination_keyboard, create_inline_kb

router = Router()
db_manager = Database()


@router.callback_query(F.data == "add_new_note")
async def add_new_note(callback: CallbackQuery,
                       state: FSMContext):
    await state.set_state(FSMContextClass.fill_title)
    await callback.message.edit_text(text="Введите название дедлайна (от 2 до 30 символов):", reply_markup=None)


@router.callback_query(F.data == "my_notes")
async def my_notes(callback: CallbackQuery):
    user_id = callback.from_user.id

    page = 0

    notes = db_manager.get_notes_by_user_id(user_id=user_id)

    total_pages = (len(notes) + 3) // 4

    if not notes:
        await callback.answer(text="У вас пока нет ни одного дедлайна.")
        return

    result_text = create_text_of_notes(notes=notes, page=page)

    reply_markup = get_pagination_keyboard(current_page=page,
                                           total_pages=total_pages)

    await callback.message.edit_text(text=result_text, reply_markup=reply_markup)


@router.callback_query(F.data.startswith("page_"))
async def pagination(callback: CallbackQuery):
    user_id = callback.from_user.id

    page = int(callback.data.split('_')[1])

    notes = db_manager.get_notes_by_user_id(user_id=user_id)

    total_pages = (len(notes) + 3) // 4

    result_text = create_text_of_notes(notes=notes, page=page)

    reply_markup = get_pagination_keyboard(current_page=page,
                                           total_pages=total_pages)

    await callback.message.edit_text(text=result_text, reply_markup=reply_markup)
