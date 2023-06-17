from source.utils.Singleton import Singleton

from pymongo import MongoClient
from os import getenv

class MongoDB(metaclass=Singleton):
    def __init__(self) -> None:
        self._db = self.__connect()

    def __connect(self):
        username = getenv("MONGODB_USERNAME")
        password = getenv("MONGODB_PASSWORD")
        host = getenv("MONGODB_HOST")
        port = getenv("MONGODB_PORT")

        if hasattr(self, "_db") and self._db is not None:
            self._db.close()

        return MongoClient(f"mongodb://{username}:{password}@{host}:{port}/?authMechanism=DEFAULT")

    def reset(self):
        self.__connect()

    def collection(self, name):
        return self._db["brofinder"].get_collection(name)
    
    @property
    def db(self):
        return self._db
    
