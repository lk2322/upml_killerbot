import functools
import random

from src.database.db import db
from src.database.models import Relationship, User


def connect_db(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db.connect(reuse_if_open=True)
        # noinspection PyBroadException
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    return wrapper


@connect_db(db)
def init_db():
    db.create_tables([User, Relationship])


@connect_db(db)
def add_user(telegram_id, name):
    user = User.create(telegram_id=telegram_id, name=name)
    user.save()


@connect_db(db)
def get_user_by_telegram_id(telegram_id):
    return User.get(User.telegram_id == telegram_id)


@connect_db(db)
def get_user_by_name(name):
    return User.get(User.name == name)


def get_user_by_id(id):
    return User.get(User.id == id)


@connect_db(db)
def get_all_users():
    return User.select()


@connect_db(db)
def get_all_alive_users():
    return User.select().where(User.is_dead == False)


@connect_db(db)
def get_all_dead_users():
    return User.select().where(User.is_dead == True)


@connect_db(db)
def get_all_relationships():
    return Relationship.select()


@connect_db(db)
def get_relationship(killer_id, victim_id):
    killer = get_user_by_id(killer_id)
    victim = get_user_by_id(victim_id)
    return Relationship.get(
        Relationship.killer == killer, Relationship.victim == victim
    )


@connect_db(db)
def add_relationship(killer_id, victim_id):
    killer = get_user_by_id(killer_id)
    victim = get_user_by_id(victim_id)
    Relationship.create(killer=killer, victim=victim)


@connect_db(db)
def remove_relationship(killer, victim):
    relationship = get_relationship(killer, victim)
    relationship.delete_instance()
    relationship.save()


@connect_db(db)
def remove_user(id):
    user = get_user_by_id(id)
    telegram_id = user.telegram_id
    user.delete_instance()
    user.save()
    return telegram_id


@connect_db(db)
def shuffle_users():
    Relationship.delete().execute()
    users = list(get_all_alive_users())
    random.shuffle(users)
    for i in range(len(users) - 1):
        add_relationship(users[i].id, users[i + 1].id)
    add_relationship(users[-1].id, users[0].id)


@connect_db(db)
def start_game():
    users = list(get_all_users())
    for user in users:
        user.is_dead = False
        user.kills = 0
        user.save()
    shuffle_users()


@connect_db(db)
def kill_user(id):
    user = get_user_by_id(id)
    user.is_dead = True
    killer_id = user.killer.get().killer_id
    killer = get_user_by_id(killer_id)
    killer.kills += 1
    killer.save()
    victim_id = user.victim.get().victim_id
    remove_relationship(killer_id, id)
    remove_relationship(id, victim_id)
    add_relationship(killer_id, victim_id)
    user.save()


@connect_db(db)
def kill_user_by_telegram_id(telegram_id):
    user = get_user_by_telegram_id(telegram_id)
    killer = user.killer.get().killer
    victim = user.victim.get().victim
    kill_user(user.id)
    return killer, victim, user
