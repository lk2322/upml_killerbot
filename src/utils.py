import logging
import os
from functools import wraps
from log import logger
import peewee
from aiogram import types


def admin_only(func):
    async def wrapper(*args):
        if args[0].from_user.id != int(os.getenv("ADMIN_ID")):
            return
        return await func(*args)

    return wrapper


def format_name(name: str):
    names = name.split()
    for i in range(len(names)):
        names[i] = names[i].capitalize()
    return " ".join(names)


def connect_db(db: peewee.Database):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            db.connect(reuse_if_open=True)
            result = func(*args, **kwargs)
            db.close()
            return result

        return wrapper

    return decorator
