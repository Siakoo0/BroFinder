from flask_restful import Resource

from abc import ABC, abstractmethod

class BaseResource(Resource):
    __name__ = "NoName"

    @property
    def urls(self):
        return ()