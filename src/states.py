import logging

import peewee
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

import msg
import utils
import db
import keyboard
from log import logger
dp: Dispatcher = ...


def register_handlers(dp_bot: Dispatcher):
    global dp
    dp = dp_bot
    dp.register_callback_query_handler(name_start, lambda c: c.data == 'button1', state="*")
    dp.register_message_handler(wait_name, state=WriteName.waiting_for_name)
    dp.register_message_handler(death_confirm, state=ConfirmDeath.confirm)


class WriteName(StatesGroup):
    waiting_for_name = State()


class ConfirmDeath(StatesGroup):
    confirm = State()


async def death_start(message: types.Message):
    user = db.get_user_by_telegram_id(message.from_user.id)
    if user.is_dead:
        await message.answer(msg.ALREADY_DEAD)
        return
    await ConfirmDeath.confirm.set()
    await dp.bot.send_message(message.from_user.id, msg.DEATH_CONFIRMATION,
                              reply_markup=keyboard.death_markup)


async def death_confirm(message: types.Message, state: FSMContext):
    if message.text == 'Да':
        killer, victim, user = db.kill_user_by_telegram_id(message.from_user.id)
        logger.info(f"{killer.name} killed {user.name} ({victim.name})")
        await dp.bot.send_message(killer.telegram_id, f"Ваша цель: {victim.name}")
        await message.answer(msg.DEATH_CONFIRMED, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Отмена", reply_markup=keyboard.main_markup)
    await state.finish()


async def name_start(callback_query: types.CallbackQuery):
    if db.get_all_relationships().count() != 0:
        await dp.bot.send_message(callback_query.from_user.id, msg.GAME_ALREADY_STARTED)
        return
    await dp.bot.send_message(callback_query.from_user.id, msg.READ_NAME_1)
    await WriteName.waiting_for_name.set()


async def wait_name(message: types.Message, state: FSMContext):
    try:
        f_name = utils.format_name(message.text)
        db.add_user(message.from_user.id, f_name)
        logger.info(f"User {f_name} added")
    except peewee.IntegrityError:
        await message.answer(msg.NAME_ALREADY_EXISTS)
        await state.finish()
        return
    await state.finish()
    await message.answer(msg.READ_NAME_2)
