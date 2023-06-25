import textwrap

import peewee
from aiogram import Bot, Dispatcher, types
from aiogram.utils.exceptions import BotBlocked, ChatNotFound

from src.database import db_funcs
from src.utils import consts
from src.utils.decorators import admin_only
from src.utils.keyboards import main_markup


@admin_only
async def check_users(message: types.Message) -> None:
    data = ''
    for user in db_funcs.get_all_users():
        alive = '❌' if user.is_dead else '✅'
        res = f"{alive} {user.id}. {user.name} - {user.kills} убийств."
        try:
            victim = user.victim.get().victim
            res += f' Жертва: {victim.id} - {victim.name}'
        except peewee.DoesNotExist:
            pass
        data += res

    for line in textwrap.wrap(data, width=consts.MESSAGE_WIDTH_LIMIT):
        await message.answer(line)

    if not data:
        await message.answer('Нет участников :(')


@admin_only
async def list_alive(message: types.Message) -> None:
    data = ''
    for user in db_funcs.get_all_alive_users():
        data += f"{user.id}. {user.name} - {user.kills} убийств\n"

    for line in textwrap.wrap(data, width=consts.MESSAGE_WIDTH_LIMIT):
        await message.answer(line)

    if not data:
        await message.answer('Нет участников :(')


@admin_only
async def delete_users(message: types.Message) -> None:
    ids = map(int, message.get_args().split())
    data = ''

    for bd_id in ids:
        try:
            tg_id = db_funcs.remove_user(bd_id)
            await message.bot.send_message(tg_id, consts.DELETED)
            data += f'Юзер *{bd_id}* (`{tg_id}`) удалён\n'
        except peewee.DoesNotExist:
            data += f'Юзера *{bd_id}* не существует\n'
        except BotBlocked:
            data += f'Юзера *{bd_id}* заблокировал бота (удалён)\n'
        except ChatNotFound:
            data += f'Нет чата с юзером *{bd_id}* (удалён)\n'

    for line in textwrap.wrap(data, width=consts.MESSAGE_WIDTH_LIMIT):
        await message.answer(line)

    if not data:
        await message.answer('Нет айдишников')


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
            data += f'Юзер *{user.id}* (`{user.telegram_id}`) заблокировал бота\n'
        except ChatNotFound:
            data += f'Нет чата с юзером *{user.id}* (`{user.telegram_id}`)\n'

    return data


@admin_only
async def start_game(message: types.Message) -> None:
    db_funcs.start_game()
    data = 'Игра началась!\n\n' + (await send_victims_to_killers())
    for line in textwrap.wrap(data, width=consts.MESSAGE_WIDTH_LIMIT):
        await message.answer(line)


@admin_only
async def shuffle(message: types.Message) -> None:
    db_funcs.shuffle_users()
    data = 'Шафл успешен!\n\n' + (await send_victims_to_killers())
    for line in textwrap.wrap(data, width=consts.MESSAGE_WIDTH_LIMIT):
        await message.answer(line)


# совместить kill и delete_users
@admin_only
async def kill(message: types.Message) -> None:
    ids = map(int, message.get_args().split())
    data = ''

    for bd_id in ids:
        try:
            tg_id = db_funcs.kill_user(bd_id)
            await message.bot.send_message(tg_id, consts.DEATH_CONFIRMED)
            data += f'Юзер *{bd_id}* (`{tg_id}`) убит\n'
        except peewee.DoesNotExist:
            data += f'Юзера *{bd_id}* не существует\n'
        except BotBlocked:
            data += f'Юзера *{bd_id}* заблокировал бота (убит)\n'
        except ChatNotFound:
            data += f'Нет чата с юзером *{bd_id}* (убит)\n'

    for line in textwrap.wrap(data, width=consts.MESSAGE_WIDTH_LIMIT):
        await message.answer(line)

    if not data:
        await message.answer('Нет айдишников')


@admin_only
async def message_to_all(message: types.Message):
    text = message.text.split(" ")[1:]
    text = " ".join(text)
    ids = db_funcs.get_all_users()
    data = 'Сообщение отправлено!\n\n'

    for user in ids:
        try:
            await message.bot.send_message(user.telegram_id, text)
        except BotBlocked:
            data += f'Юзер *{user.id}* (`{user.telegram_id}`) заблокировал бота\n'
        except ChatNotFound:
            data += f'Нет чата с юзером *{user.id}* ({user.telegram_id})\n'

    for line in textwrap.wrap(data, width=consts.MESSAGE_WIDTH_LIMIT):
        await message.answer(line)


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(check_users, commands=['check_users'])
    dp.register_message_handler(list_alive, commands=['list_alive'])
    dp.register_message_handler(delete_users, commands=['delete_users'])
    dp.register_message_handler(start_game, commands=['start_game'])
    dp.register_message_handler(shuffle, commands=['shuffle'])
    dp.register_message_handler(kill, commands=['kill'])
    dp.register_message_handler(message_to_all, commands=['message'])
