from source.api.BaseResource import BaseResource
from source.api.models.User import User
from playhouse.shortcuts import model_to_dict
import json

class UserResource(BaseResource):
    
    @property
    def urls(self):
        return ("/test/<int:user_id>")

    def get(self, user_id):
        return {"ok" : model_to_dict(User.get(User.id == user_id))}