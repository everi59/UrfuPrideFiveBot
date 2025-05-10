from dataclasses import dataclass
from typing import Any

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, KeyboardButton, InlineKeyboardMarkup
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


def create_keyboard(buttons: list,
                    width: int | None = None,
                    adjust: list | None = None,
                    one_time_keyboard: True | False = False):
    kb_builder = ReplyKeyboardBuilder()
    buttons = [KeyboardButton(text=button) for button in buttons]
    if width:
        kb_builder.row(*buttons, width=width)
    else:
        kb_builder.add(*buttons)
        kb_builder.adjust(*adjust)
    return kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=one_time_keyboard)


def get_pagination_keyboard(current_page, total_pages):
    kb_builder = InlineKeyboardBuilder()

    buttons = []

    if current_page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{current_page - 1}"))
    else:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"nope"))

    buttons.append(InlineKeyboardButton(text=f"{current_page + 1}/{total_pages}", callback_data="nope"))

    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"page_{current_page + 1}"))
    else:
        buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"nope"))

    kb_builder.row(*buttons, width=3)
    return kb_builder.as_markup()
