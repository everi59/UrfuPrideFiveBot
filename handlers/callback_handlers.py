from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config.config import Config, load_config
from services.services import FSMContextClass
from data.database import Database

router = Router()
db_manager = Database()


@router.callback_query(F.data == "add_new_note")
async def add_new_note(callback: CallbackQuery,
                       state: FSMContext):
    await state.set_state(FSMContextClass.fill_title)
    await callback.message.edit_text(text="Введите название дедлайна (от 2 до 30 символов):")
    await callback.message.edit_reply_markup(reply_markup=None)

