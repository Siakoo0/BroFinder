from source.api.models.BaseModel import BaseModel
from peewee import BigIntegerField, SmallIntegerField

class User(BaseModel):
    id = BigIntegerField(primary_key=True)
    role = SmallIntegerField(null=False)