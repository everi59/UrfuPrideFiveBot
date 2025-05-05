from aiogram import Bot
from aiogram.types import BotCommand

import re
from re import Match

from keyboards.keyboards import PointsCallbackFactory
from aiogram.fsm.state import State, StatesGroup


def check_title(title: str) -> Match[str] | None:
    return re.fullmatch(r"""[а-яА-Яa-zA-Z0-9-]{2,30}""", title)