import functools

from src.utils.consts import Config


def admin_only(func):
    @functools.wraps(func)
    async def wrapper(*args):
        if args[0].from_user.id not in Config.ADMINS:
            return
        return await func(*args)

    return wrapper
