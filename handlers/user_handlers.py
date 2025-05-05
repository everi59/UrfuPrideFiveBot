from aiogram import Router
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message
from keyboards.keyboards import create_inline_kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from config.config import Config, load_config
from services.services import get_points
from random import randint

config: Config = load_config()
router = Router()


# START_COMMAND
@router.message(CommandStart(), StateFilter(default_state))
async def start(message: Message):
    await message.answer(text='Привет.')
