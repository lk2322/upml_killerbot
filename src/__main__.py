from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from src.database import db_funcs
from src.handlers.admin import register_admin_handlers
from src.handlers.client import register_client_handlers
from src.handlers.states import register_state_handlers
from src.utils.consts import Config


async def on_startup(dp: Dispatcher) -> None:
    db_funcs.init_db()
    register_admin_handlers(dp)
    register_client_handlers(dp)
    register_state_handlers(dp)


def main():
    bot = Bot(token=Config.TOKEN, parse_mode="markdown")
    dp = Dispatcher(bot, storage=MemoryStorage())
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == "__main__":
    main()
