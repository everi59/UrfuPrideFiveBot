from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from config.config import Config, load_config
from keyboards.keyboards import create_inline_kb, PointsCallbackFactory
from services.services import get_points
from random import randint

config: Config = load_config()
router = Router()
