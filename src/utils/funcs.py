import functools
from typing import Iterable

from src.database import db_funcs
from src.utils import consts
from src.utils.consts import Config, TG_ID


def admin_only(func):
    """
    Декоратор для тех функций-обработчиков,
    которые используются только админами бота.
    """

    @functools.wraps(func)
    async def wrapper(*args):
        if args[0].from_user.id not in Config.ADMINS:
            return
        return await func(*args)

    return wrapper


def game_started(func):
    """
    Декоратор для тех функций-обработчиков,
    которые используются только во время запущенной игры.
    """

    @functools.wraps(func)
    async def wrapper(*args):
        if not is_game_started():
            return
        return await func(*args)

    return wrapper


def tg_click_name(username: str | int, user_id: TG_ID) -> str:
    """
    Возвращает markdown строку с упоминанием пользователя.

    :param username: Отображаемое имя.
    :param user_id: ТГ Айди.
    """
    return f"[{username}](tg://user?id={user_id})"


def wrap(text: list[str]) -> Iterable[str]:
    """
    Обрезка списка с строками по лимиту телеграмма для отправки в нескольк сообщений.

    :param text: Сообщение.
    :return: Сообщения.
    """
    if not text:
        return ""

    text = text.copy()
    line = ""
    while text:
        while text and len(line + text[0]) < consts.MESSAGE_WIDTH_LIMIT:
            line += text.pop(0) + "\n"
        yield line
        line = ""


def is_game_started() -> bool:
    """
    Началась (Запущена) ли игра.
    """
    return bool(db_funcs.get_all_relationships().count())
