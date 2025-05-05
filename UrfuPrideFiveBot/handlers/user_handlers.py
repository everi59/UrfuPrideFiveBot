from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message
from keyboards.keyboards import create_keyboard
from aiogram.fsm.state import default_state
from UrfuPrideFiveBot.config.config import Config, load_config

config: Config = load_config()
router = Router()


# START_COMMAND
@router.message(CommandStart(), StateFilter(default_state))
async def start(message: Message):
    if message.from_user.id in get_users_ids():
        await message.answer(text='Привет! Я помогу тебе следить за дедлайнами и домашними заданиями.')
    await message.answer(text='Выбери нужное действие:\n1. Добавить новый дедлайн.\n2. Просмотр дедлайнов.',
                         reply_markup=create_keyboard(['1', '2'], width=2, one_time_keyboard=True))
