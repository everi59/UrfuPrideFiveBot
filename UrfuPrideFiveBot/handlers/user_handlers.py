from aiogram import Router
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message
from keyboards.keyboards import create_keyboard, create_inline_kb
from aiogram.fsm.state import default_state
from UrfuPrideFiveBot.config.config import Config, load_config

config: Config = load_config()
router = Router()


# START_COMMAND
@router.message(CommandStart(), StateFilter(default_state))
async def start(message: Message):
    if not (message.from_user.id in [0]):
        await message.answer(text='Привет! Я помогу тебе следить за дедлайнами и домашними заданиями.')
    await message.answer(text='Выбери нужное действие',
                         reply_markup=create_inline_kb(width=1, dct={'add_new_note': 'Добавить новый дедлайн',
                                                                     'my_notes': 'Просмотр дедлайнов'}))


# HELP_COMMAND
@router.message(Command(commands='help'))
async def command_help(message: Message):
    await message.answer(text='Это бот для удобного хранения дедлайнов.\nЧтобы добавить новый дедлайн или посмотреть '
                              'текущие нажми /start')
