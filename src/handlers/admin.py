from typing import Callable, Iterable

import peewee
from aiogram import Bot, Dispatcher, types
from aiogram.utils.exceptions import BotBlocked, ChatNotFound

from src.database import db_funcs
from src.database.models import User
from src.utils.consts import DB_ID, DELETED, DEATH_CONFIRMED
from src.utils.funcs import (
    admin_only,
    game_started,
    is_game_started,
    tg_click_name,
    wrap,
)
from src.utils.keyboards import main_markup


async def disqualification(
    ids: Iterable[DB_ID],
    function: Callable[[DB_ID], User],
    bot: Bot,
    message_to_users: str,
    action: str,
) -> list[str]:
    data = []

    for db_id in ids:
        try:
            user = function(db_id)
        except peewee.DoesNotExist:
            data.append(f"Юзера *{db_id}* не существует")
            continue

        try:
            await bot.send_message(user.telegram_id, message_to_users)
            data.append(f"Юзер {tg_click_name(db_id, user.telegram_id)} {action}")
        except BotBlocked:
            data.append(
                f"Юзер {tg_click_name(db_id, user.telegram_id)} "
                f"заблокировал бота ({action})"
            )
        except ChatNotFound:
            data.append(
                f"Нет чата с юзером "
                f"{tg_click_name(db_id, user.telegram_id)} ({action})"
            )

    return data


async def send_victims_to_killers(bot: Bot) -> list[str]:
    data = []

    for user in db_funcs.get_all_alive_users():
        try:
            await bot.send_message(
                user.telegram_id,
                f"Ваша цель: {user.victim.get().victim.name}",
                reply_markup=main_markup,
            )
        except BotBlocked:
            data.append(
                f"Юзер {tg_click_name(user.id, user.telegram_id)} заблокировал бота"
            )
        except ChatNotFound:
            data.append(f"Нет чата с юзером {tg_click_name(user.id, user.telegram_id)}")

    return data


@admin_only
async def check_users(message: types.Message) -> None:
    data = []
    for user in db_funcs.get_all_users():
        alive = "❌" if user.is_dead else "✅"
        res = (
            f"{alive} {user.id}. {tg_click_name(user.name, user.telegram_id)} - "
            f"{user.kills} убийств."
        )
        try:
            victim = user.victim.get().victim
            res += (
                f" Жертва: {victim.id} - "
                f"{tg_click_name(victim.name, victim.telegram_id)}"
            )
        except peewee.DoesNotExist:
            pass
        data.append(res)

    for line in wrap(data):
        await message.answer(line)

    if not data:
        await message.answer("Нет участников :(")


@admin_only
@game_started
async def list_alive(message: types.Message) -> None:
    data = []
    for user in db_funcs.get_all_alive_users():
        data.append(
            f"{user.id}. "
            f"{tg_click_name(user.name, user.telegram_id)} - {user.kills} убийств"
        )

    for line in wrap(data):
        await message.answer(line)

    if not data:
        await message.answer("Нет участников :(")


@admin_only
async def delete_users(message: types.Message) -> None:
    if is_game_started():  # Во время игры только убивать, иначе смэрть
        return

    ids = map(int, message.get_args().split())

    func = db_funcs.remove_user
    data = await disqualification(ids, func, message.bot, DELETED, "удалён")

    for line in wrap(data):
        await message.answer(line)

    if not data:
        await message.answer("Нет айдишников")


@admin_only
@game_started
async def kill(message: types.Message) -> None:
    ids = map(int, message.get_args().split())

    func = db_funcs.kill_user_by_id
    data = await disqualification(ids, func, message.bot, DEATH_CONFIRMED, "убит")

    for line in wrap(data):
        await message.answer(line)

    if not data:
        await message.answer("Нет айдишников")


@admin_only
async def start_game(message: types.Message) -> None:
    db_funcs.start_game()
    data = ["Игра началась!\n"] + await send_victims_to_killers(message.bot)
    for line in wrap(data):
        await message.answer(line)


@admin_only
@game_started
async def shuffle(message: types.Message) -> None:
    db_funcs.shuffle_users()
    data = ["Шафл успешен!\n"] + await send_victims_to_killers(message.bot)
    for line in wrap(data):
        await message.answer(line)


@admin_only
async def message_to_all(message: types.Message):
    text = message.text.split(" ")[1:]
    text = " ".join(text)
    data = ["Сообщение отправлено!\n"]

    for user in db_funcs.get_all_users():
        try:
            await message.bot.send_message(user.telegram_id, text)
        except BotBlocked:
            data.append(
                f"Юзер {tg_click_name(user.id, user.telegram_id)} заблокировал бота\n"
            )
        except ChatNotFound:
            data.append(f"Нет чата с юзером {tg_click_name(user.id, user.telegram_id)}")

    for line in wrap(data):
        await message.answer(line)


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(check_users, commands=["check_users"])
    dp.register_message_handler(list_alive, commands=["list_alive"])
    dp.register_message_handler(delete_users, commands=["delete_users"])
    dp.register_message_handler(start_game, commands=["start_game"])
    dp.register_message_handler(shuffle, commands=["shuffle"])
    dp.register_message_handler(kill, commands=["kill"])
    dp.register_message_handler(message_to_all, commands=["message"])
