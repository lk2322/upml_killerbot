from peewee import SqliteDatabase

from src.utils.consts import Config


db = SqliteDatabase(Config.DB_FILE, pragmas={"foreign_keys": 1})
