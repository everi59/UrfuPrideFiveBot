from dataclasses import dataclass
from typing import Any

from aiogram.filters.callback_data import CallbackData
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import keyboard_lexicon


def create_inline_kb(width: int,
                     *args: str,
                     lst: list | None = None,
                     last_btn: str | None = None,
                     dct: dict | None = None,
                     back_button: Any | None = None,
                     **kwargs: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if lst:
        for button in lst:
            buttons.append(InlineKeyboardButton(
                text=keyboard_lexicon[button] if button in keyboard_lexicon else button,
                callback_data=button))
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=keyboard_lexicon[button] if button in keyboard_lexicon else button,
                callback_data=button))
    if dct:
        for button, text in dct.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))
    kb_builder.row(*buttons, width=width)
    if last_btn:
        kb_builder.row(InlineKeyboardButton(
            text=keyboard_lexicon[last_btn] if last_btn in keyboard_lexicon else last_btn,
            callback_data=last_btn
        ))
    if back_button:
        kb_builder.row(InlineKeyboardButton(
            text='Назад',
            callback_data=back_button
        ))
    return kb_builder.as_markup()


@dataclass
class PointsCallbackFactory(CallbackData, prefix='Points'):
    film: str
    point: int

    def __init__(self, film, point):
        super().__init__(film=film, point=point)
