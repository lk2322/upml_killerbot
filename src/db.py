import peewee
import os
import utils
import dotenv
import random

dotenv.load_dotenv()
print(os.getenv('DB_FILE'))
db = peewee.SqliteDatabase(os.getenv('DB_FILE'), pragmas={'foreign_keys': 1})


class User(peewee.Model):
    telegram_id = peewee.IntegerField(unique=True)
    name = peewee.CharField()
    kills = peewee.IntegerField(default=0)
    is_dead = peewee.BooleanField(default=False)

    class Meta:
        database = db


class Relationship(peewee.Model):
    killer = peewee.ForeignKeyField(User, backref='victim', unique=False)
    victim = peewee.ForeignKeyField(User, backref='killer', unique=False)

    class Meta:
        database = db


@utils.connect_db(db)
def init_db():
    db.create_tables([User, Relationship])


@utils.connect_db(db)
def add_user(telegram_id, name):
    user = User.create(telegram_id=telegram_id, name=name)
    user.save()


@utils.connect_db(db)
def get_user_by_telegram_id(telegram_id):
    return User.get(User.telegram_id == telegram_id)


@utils.connect_db(db)
def get_user_by_name(name):
    return User.get(User.name == name)


def get_user_by_id(id):
    return User.get(User.id == id)


@utils.connect_db(db)
def get_all_users():
    return User.select()


@utils.connect_db(db)
def get_all_alive_users():
    return User.select().where(User.is_dead == False)


@utils.connect_db(db)
def get_all_dead_users():
    return User.select().where(User.is_dead is True)


@utils.connect_db(db)
def get_all_relationships():
    return Relationship.select()


@utils.connect_db(db)
def get_relationship(killer_id, victim_id):
    killer = get_user_by_id(killer_id)
    victim = get_user_by_id(victim_id)
    return Relationship.get(Relationship.killer == killer, Relationship.victim == victim)


@utils.connect_db(db)
def add_relationship(killer_id, victim_id):
    killer = get_user_by_id(killer_id)
    victim = get_user_by_id(victim_id)
    Relationship.create(killer=killer, victim=victim)


@utils.connect_db(db)
def remove_relationship(killer, victim):
    relationship = get_relationship(killer, victim)
    relationship.delete_instance()
    relationship.save()


@utils.connect_db(db)
def remove_user(id):
    user = get_user_by_id(id)
    telegram_id = user.telegram_id
    user.delete_instance()
    user.save()
    return telegram_id


@utils.connect_db(db)
def shuffle_users():
    Relationship.delete().execute()
    users = list(get_all_alive_users())
    random.shuffle(users)
    for i in range(len(users) - 1):
        add_relationship(users[i].id, users[i + 1].id)
    add_relationship(users[-1].id, users[0].id)


@utils.connect_db(db)
def start_game():
    Relationship.delete().execute()
    users = list(get_all_users())
    random.shuffle(users)
    for i in range(len(users) - 1):
        users[i].is_dead = False
        users[i].kills = 0
        users[i].save()
        add_relationship(users[i].id, users[i + 1].id)
    add_relationship(users[-1].id, users[0].id)


@utils.connect_db(db)
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


@utils.connect_db(db)
def kill_user_by_telegram_id(telegram_id):
    user = get_user_by_telegram_id(telegram_id)
    killer = user.killer.get().killer
    victim = user.victim.get().victim
    kill_user(user.id)
    return killer, victim, user
