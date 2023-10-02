import functools
import random

from src.database.db import db
from src.database.models import Relationship, User
from src.utils.consts import DB_ID, TG_ID


def connect_db(func):
    """
    Декоратор для подключения к бдшке перед выполнением функций,
    связанных с ней.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db.connect(reuse_if_open=True)
        # noinspection PyBroadException
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            try:
                db.rollback()
            except AttributeError:
                pass
            raise e
        finally:
            db.close()

    return wrapper


@connect_db
def init_db() -> None:
    db.create_tables([User, Relationship])


@connect_db
def add_user(telegram_id: TG_ID, name: str) -> None:
    user = User.create(telegram_id=telegram_id, name=name)
    user.save()


@connect_db
def add_relationship(killer_id: DB_ID, victim_id: DB_ID) -> None:
    killer = get_user_by_id(killer_id)
    victim = get_user_by_id(victim_id)
    relationship = Relationship.create(killer=killer, victim=victim)
    relationship.save()


@connect_db
def get_user_by_telegram_id(telegram_id: TG_ID) -> User | None:
    return User.get_or_none(User.telegram_id == telegram_id)


def get_user_by_id(db_id: DB_ID) -> User | None:
    return User.get_or_none(User.id == db_id)


@connect_db
def get_all_users():
    return User.select()


@connect_db
def get_all_alive_users():
    return User.select().where(User.is_dead == False)


@connect_db
def get_all_relationships():
    return Relationship.select()


@connect_db
def get_relationship(killer: DB_ID, victim: DB_ID) -> Relationship:
    killer = get_user_by_id(killer)
    victim = get_user_by_id(victim)
    return Relationship.get(
        Relationship.killer == killer, Relationship.victim == victim
    )


@connect_db
def remove_relationship(killer: DB_ID, victim: DB_ID) -> None:
    relationship = get_relationship(killer, victim)
    relationship.delete_instance()
    relationship.save()


@connect_db
def remove_user(db_id: DB_ID) -> User:
    user = get_user_by_id(db_id)
    user.delete_instance()
    user.save()
    return user


@connect_db
def start_game() -> None:
    for user in get_all_users():
        user.is_dead = False
        user.kills = 0
        user.save()
    shuffle_users()


@connect_db
def shuffle_users() -> None:
    Relationship.delete().execute()
    users = list(get_all_alive_users())
    random.shuffle(users)
    for i in range(len(users) - 1):
        add_relationship(users[i].id, users[i + 1].id)
    add_relationship(users[-1].id, users[0].id)


@connect_db
def kill_user_by_id(db_id: DB_ID) -> User:
    user = get_user_by_id(db_id)
    user.is_dead = True
    user.save()

    killer_id = user.killer.get().killer_id
    killer = get_user_by_id(killer_id)
    killer.kills += 1
    killer.save()

    victim_id = user.victim.get().victim_id
    remove_relationship(killer_id, db_id)
    remove_relationship(db_id, victim_id)
    add_relationship(killer_id, victim_id)

    return user


@connect_db
def kill_user_by_telegram_id(telegram_id: TG_ID) -> tuple[User, User, User]:
    user = get_user_by_telegram_id(telegram_id)
    killer = user.killer.get().killer
    victim = user.victim.get().victim
    kill_user_by_id(user.id)
    return killer, victim, user
