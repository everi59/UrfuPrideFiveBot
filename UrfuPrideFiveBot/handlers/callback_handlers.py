from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from config.config import Config, load_config

config: Config = load_config()
router = Router()


@router.callback_query(F.data == "add_new_note")
async def add_new_note(callback: CallbackQuery,
                       state: FSMContext):
    # await state.set_state()
    await callback.answer(text="Введи название задачи.")
