from peewee import SqliteDatabase, Model

db = SqliteDatabase("BroFinder.db")

class BaseModel(Model):
    class Meta:
        loaded_entities = False
        database = db