from aiogram import Dispatcher, types

from src.database import db_funcs
from src.handlers import states
from src.utils import consts
from src.utils.funcs import game_started
from src.utils.keyboards import inline_join, main_markup


async def send_welcome(message: types.Message):
    await message.answer(consts.WELCOME, reply_markup=inline_join)


@game_started
async def target(message: types.Message):
    if message.text == consts.TextCommands.CONFIRM_DEATH:
        await states.death_start(message)
        return

    if message.text == consts.TextCommands.REMIND_VICTIM:
        user = db_funcs.get_user_by_telegram_id(message.from_user.id)
        if user.is_dead:
            await message.answer(consts.YOU_ARE_DEAD)
        else:
            await message.answer(
                f"Ваша цель: {user.victim.get().victim.name}",
                reply_markup=main_markup,
            )


def register_client_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(send_welcome, commands=["start", "help"])
    dp.register_message_handler(target)
