import logging
import os

import aiogram.utils.exceptions
import peewee
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import keyboard
import msg
import states
import db
load_dotenv()
API_TOKEN = os.getenv("TOKEN")


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(msg.WELCOME, reply_markup=keyboard.inline_join)


@dp.message_handler(commands=['check_users'])
async def check_users(message: types.Message):
    if message.from_user.id != int(os.getenv("ADMIN_ID")):
        return
    res = ""
    for i in db.get_all_users():
        try:
            res += f"{i.id}. {i.name} - {i.kills} kills - {i.is_dead} Жертва: {i.victim.get().victim.name}\n"
        except peewee.DoesNotExist:
            res += f"{i.id}. {i.name} - {i.kills} kills - {i.is_dead}\n"
    if res == "":
        res = "No users"
    await message.answer(res)


@dp.message_handler(commands=['delete_users'])
async def delete_users(message: types.Message):
    if message.from_user.id != int(os.getenv("ADMIN_ID")):
        return
    ids = message.text.split()[1:]
    for i in ids:
        try:
            db.remove_user(int(i))
        except peewee.DoesNotExist:
            await message.answer(f"User with id {i} does not exist")
    await message.answer("Deleted")


@dp.message_handler(commands=['start_game'])
async def start_game(message: types.Message):
    if message.from_user.id != int(os.getenv("ADMIN_ID")):
        return
    db.start_game()
    for i in db.get_all_users():
        try:
            await bot.send_message(i.telegram_id, f"Ваша цель: {i.victim.get().victim.name}",
                                   reply_markup=keyboard.main_markup)
        except aiogram.utils.exceptions.ChatNotFound:
            await message.answer(f"User with id {i.telegram_id} does not exist")
    await message.answer("Game started")


@dp.message_handler(commands=['shuffle'])
async def shuffle(message: types.Message):
    if message.from_user.id != int(os.getenv("ADMIN_ID")):
        return
    db.shuffle_users()
    for i in db.get_all_alive_users():
        try:
            await bot.send_message(i.telegram_id, f"Ваша цель: {i.victim.get().victim.name}",
                                   reply_markup=keyboard.main_markup)
        except aiogram.utils.exceptions.ChatNotFound:
            await message.answer(f"User with id {i.telegram_id} does not exist")
    await message.answer("Shuffled")


@dp.message_handler(commands=['kill'])
async def kill(message: types.Message):
    if message.from_user.id != int(os.getenv("ADMIN_ID")):
        return
    ids = message.text.split()[1:]
    for i in ids:
        try:
            db.kill_user(int(i))
            user = db.get_user_by_id(int(i))
            await bot.send_message(user.telegram_id, "Вы умерли")
        except peewee.DoesNotExist:
            await message.answer(f"User with id {i} does not exist")
    await message.answer("Killed")


@dp.message_handler(commands=['message'])
async def message_to_all(message: types.Message):
    if message.from_user.id != int(os.getenv("ADMIN_ID")):
        return
    text = message.text.split()[1:]
    text = " ".join(text)
    ids = db.get_all_users()
    for i in ids:
        try:
            await bot.send_message(i.telegram_id, text)
        except peewee.DoesNotExist:
            await message.answer(f"User with id {i.id} does not exist")
    await message.answer("Sent")


@dp.message_handler()
async def target(message: types.Message):
    if db.get_all_relationships().count() == 0:
        return
    user = db.get_user_by_telegram_id(message.from_user.id)
    if message.text == "Подтвердить смерть☠":
        await states.death_start(message)
    elif message.text == "Напомнить цель🔪":
        if user.is_dead:
            await message.answer("Вы мертвы")
        else:
            await message.answer(f"Ваша цель: {user.victim.get().victim.name}")


states.register_handlers(dp)
if __name__ == '__main__':
    db.init_db()
    executor.start_polling(dp, skip_updates=True)
