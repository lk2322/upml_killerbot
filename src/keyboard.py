from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton

__button_join = InlineKeyboardButton('Участвовать', callback_data='button1')
inline_join = InlineKeyboardMarkup()
inline_join.add(__button_join)

__button_death = KeyboardButton('Подтвердить смерть☠')
__button_victim = KeyboardButton('Напомнить цель🔪')
main_markup = ReplyKeyboardMarkup(resize_keyboard=True)
main_markup.add(__button_death, __button_victim)

__button_death_confirm = KeyboardButton('Да')
__button_death_cancel = KeyboardButton('Нет')
death_markup = ReplyKeyboardMarkup(resize_keyboard=True)
death_markup.add(__button_death_confirm, __button_death_cancel)