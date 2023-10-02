from peewee import (
    BooleanField,
    CharField,
    ForeignKeyField,
    IntegerField,
    Model,
)

from src.database.db import db


class BaseModel(Model):
    id = IntegerField(primary_key=True, unique=True)

    class Meta:
        database = db


class User(BaseModel):
    telegram_id = IntegerField(unique=True)
    name = CharField(unique=True)
    kills = IntegerField(default=0)
    is_dead = BooleanField(default=False)


class Relationship(BaseModel):
    killer = ForeignKeyField(User, backref="victim", unique=False)
    victim = ForeignKeyField(User, backref="killer", unique=False)
