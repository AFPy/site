from peewee import Model

from afpy import database


class BaseModel(Model):
    class Meta:
        database = database
