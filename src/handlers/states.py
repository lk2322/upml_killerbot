import peewee
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from src.database import db_funcs
from src.logs import logger
from src.utils import consts
from src.utils.consts import CallbackData
from src.utils.funcs import is_game_started
from src.utils.keyboards import death_markup, main_markup


class WriteName(StatesGroup):
    waiting_for_name = State()


class ConfirmDeath(StatesGroup):
    confirm = State()


async def name_start(callback: types.CallbackQuery):
    await callback.answer()

    if is_game_started():
        await callback.bot.send_message(
            callback.from_user.id, consts.GAME_ALREADY_STARTED
        )
        return
    if db_funcs.get_user_by_telegram_id(callback.from_user.id):
        await callback.bot.send_message(callback.from_user.id, consts.ALREADY_PLAYING)

    await callback.bot.send_message(callback.from_user.id, consts.READ_NAME_1)
    await WriteName.waiting_for_name.set()


async def wait_name(message: types.Message, state: FSMContext):
    if is_game_started():  # Начал name_start до начала игры, ввёл имя после начала
        await state.finish()
        return

    # Первые три слова и максимум 255 символов
    full_name = " ".join(word.capitalize() for word in message.text.split()[:3])[:255]

    try:
        db_funcs.add_user(message.from_user.id, full_name)
        logger.info(f'Юзер "{full_name}" добавлен')
        await message.answer(consts.READ_NAME_2)
    except peewee.IntegrityError:
        await message.answer(consts.NAME_ALREADY_EXISTS)

    await state.finish()


async def death_start(message: types.Message):
    user = db_funcs.get_user_by_telegram_id(message.from_user.id)

    if user.is_dead:
        await message.answer(consts.ALREADY_DEAD)
        return

    await ConfirmDeath.confirm.set()
    await message.answer(consts.ARE_YOU_SURE_DEATH_CONFIRM, reply_markup=death_markup)


async def death_confirm(message: types.Message, state: FSMContext):
    if message.text == consts.TextCommands.YES:
        killer, victim, user = db_funcs.kill_user_by_telegram_id(message.from_user.id)
        logger.info(f'"{killer.name}" убил "{user.name}" ("{victim.name}")')
        await message.bot.send_message(killer.telegram_id, f"Ваша цель: {victim.name}")
        await message.answer(consts.DEATH_CONFIRMED, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Отмена", reply_markup=main_markup)

    await state.finish()


def register_state_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        name_start,
        lambda c: c.data == CallbackData.JOIN_THE_GAME,
        state="*",
    )
    dp.register_message_handler(wait_name, state=WriteName.waiting_for_name)
    dp.register_message_handler(death_confirm, state=ConfirmDeath.confirm)
