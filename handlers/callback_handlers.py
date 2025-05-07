from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config.config import Config, load_config
from services.services import FSMContextClass

config: Config = load_config()
router = Router()


@router.callback_query(F.data == "add_new_note")
async def add_new_note(callback: CallbackQuery,
                       state: FSMContext):
    await state.set_state(FSMContextState.fill_title)
    await callback.answer(text="Введите название дедлайна (от 2 до 30 символов):")

