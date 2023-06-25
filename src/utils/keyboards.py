from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from src.utils.consts import CallbackData, TextCommands


inline_join = InlineKeyboardMarkup().add(
    InlineKeyboardButton(
        '🩸Участвовать',
        callback_data=CallbackData.JOIN_THE_GAME
    )
)

main_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(TextCommands.CONFIRM_DEATH),
    KeyboardButton(TextCommands.REMIND_VICTIM)
)

death_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(TextCommands.YES),
    KeyboardButton(TextCommands.NO)
)
