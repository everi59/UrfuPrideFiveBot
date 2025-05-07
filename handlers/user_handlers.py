from aiogram import Router
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from keyboards.keyboards import create_inline_kb
from config.config import Config, load_config
from config.config import FSMContextClass

config: Config = load_config()
router = Router()


# START_COMMAND
@router.message(CommandStart(), StateFilter(default_state))
async def start(message: Message,
                state: FSMContext):
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


@router.message(StateFilter(FSMContextClass))
async def fill_title(message: Message,
                     state: FSMContext):
    title = message.text.strip()
