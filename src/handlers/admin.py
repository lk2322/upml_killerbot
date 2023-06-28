from typing import Callable, Iterable

import peewee
from aiogram import Bot, Dispatcher, types
from aiogram.utils.exceptions import BotBlocked, ChatNotFound

from src.database import db_funcs
from src.database.models import User
from src.utils import consts
from src.utils.consts import DB_ID
from src.utils.funcs import (
    admin_only, game_started, is_game_started,
    tg_click_name, wrap,
)
from src.utils.keyboards import main_markup


async def disqualification(
        ids: Iterable[DB_ID],
        function: Callable[[DB_ID], User],
        bot: Bot,
        message_to_users: str,
        action: str
) -> str:
    data = ''

    for db_id in ids:
        try:
            user = function(db_id)
        except peewee.DoesNotExist:
            data += f'Юзера *{db_id}* не существует\n'
            continue

        try:
            await bot.send_message(user.telegram_id, message_to_users)
            data += f'Юзер {tg_click_name(db_id, user.telegram_id)} {action}\n'
        except BotBlocked:
            data += f'Юзер {tg_click_name(db_id, user.telegram_id)} заблокировал бота ({action})\n'
        except ChatNotFound:
            data += f'Нет чата с юзером {tg_click_name(db_id, user.telegram_id)} ({action})\n'

    return data


async def send_victims_to_killers() -> str:
    data = ''
    bot = Bot.get_current(no_error=False)

    for user in db_funcs.get_all_users():
        try:
            await bot.send_message(
                user.telegram_id,
                f"Ваша цель: {user.victim.get().victim.name}",
                reply_markup=main_markup
            )
        except BotBlocked:
            data += f'Юзер {tg_click_name(user.id, user.telegram_id)} заблокировал бота\n'
        except ChatNotFound:
            data += f'Нет чата с юзером {tg_click_name(user.id, user.telegram_id)}\n'

    return data


@admin_only
async def check_users(message: types.Message) -> None:
    data = ''
    for user in db_funcs.get_all_users():
        alive = '❌' if user.is_dead else '✅'
        res = f"{alive} {user.id}. {tg_click_name(user.name, user.telegram_id)} - {user.kills} убийств."
        try:
            victim = user.victim.get().victim
            res += f' Жертва: {victim.id} - {tg_click_name(victim.name, victim.telegram_id)}'
        except peewee.DoesNotExist:
            pass
        data += res + '\n'

    for line in wrap(data):
        await message.answer(line)

    if not data:
        await message.answer('Нет участников :(')


@admin_only
@game_started
async def list_alive(message: types.Message) -> None:
    data = ''
    for user in db_funcs.get_all_alive_users():
        data += f"{user.id}. {tg_click_name(user.name, user.telegram_id)} - {user.kills} убийств\n"

    for line in wrap(data):
        await message.answer(line)

    if not data:
        await message.answer('Нет участников :(')


@admin_only
async def delete_users(message: types.Message) -> None:
    if is_game_started():  # Во время игры только убивать, иначе смэрть
        return

    ids = map(int, message.get_args().split())

    func = db_funcs.remove_user
    data = await disqualification(
        ids, func, message.bot, consts.DELETED, 'удалён'
    )

    for line in wrap(data):
        await message.answer(line)

    if not data:
        await message.answer('Нет айдишников')


@admin_only
@game_started
async def kill(message: types.Message) -> None:
    ids = map(int, message.get_args().split())

    func = db_funcs.kill_user_by_id
    data = await disqualification(
        ids, func, message.bot, consts.DEATH_CONFIRMED, 'убит'
    )

    for line in wrap(data):
        await message.answer(line)

    if not data:
        await message.answer('Нет айдишников')


@admin_only
async def start_game(message: types.Message) -> None:
    db_funcs.start_game()
    data = 'Игра началась!\n\n' + (await send_victims_to_killers())
    for line in wrap(data):
        await message.answer(line)


@admin_only
@game_started
async def shuffle(message: types.Message) -> None:
    db_funcs.shuffle_users()
    data = 'Шафл успешен!\n\n' + (await send_victims_to_killers())
    for line in wrap(data):
        await message.answer(line)


@admin_only
async def message_to_all(message: types.Message):
    text = message.text.split(" ")[1:]
    text = " ".join(text)
    data = 'Сообщение отправлено!\n\n'

    for user in db_funcs.get_all_users():
        try:
            await message.bot.send_message(user.telegram_id, text)
        except BotBlocked:
            data += f'Юзер {tg_click_name(user.id, user.telegram_id)} заблокировал бота\n'
        except ChatNotFound:
            data += f'Нет чата с юзером {tg_click_name(user.id, user.telegram_id)}\n'

    for line in wrap(data):
        await message.answer(line)


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(check_users, commands=['check_users'])
    dp.register_message_handler(list_alive, commands=['list_alive'])
    dp.register_message_handler(delete_users, commands=['delete_users'])
    dp.register_message_handler(start_game, commands=['start_game'])
    dp.register_message_handler(shuffle, commands=['shuffle'])
    dp.register_message_handler(kill, commands=['kill'])
    dp.register_message_handler(message_to_all, commands=['message'])
