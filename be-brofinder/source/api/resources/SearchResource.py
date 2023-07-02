from datetime import datetime
from redis import Redis
from json import dumps, loads

from source.api.BaseResource import BaseResource
from source.utils.MongoDB import MongoDB

from source.entities.Search import Search

from source.api.dto.SearchDTO import SearchDTO


class SearchResource(BaseResource):
    @property
    def urls(self):
        return ('/api/search', )
    
    def publish(self, data):
        # TODO: Da sostituire con .env

        red = Redis("192.168.1.232", port=6379, charset="utf-8", decode_responses=True)
        red.ping()
        
        red.lpush("search_queue", dumps(data, default=str))
        
        red.publish("crawler/search_queue", "New Item Loaded")
    
    def post(self):
        rules = {
            "text" : {
                "type" : str,
                "required" : True,
                "location" : "form",
                "help" : "Il campo 'text' risulta essere obbligatorio, ma non è stato passato."
            },
            "price" : {
                "type" : int,
                "default": None,
                "location" : "form"
            },
            "user" : {
                "type" : int,
                "required" : True,
                "location" : "form",
                "help" : "Il campo 'user' risulta essere obbligatorio, ma non è stato passato."
            },
            "forward" : {
                "type" : bool,
                "default": False,
                "location" : "form"
            },
            "publish_at": {
                "type" : lambda x: datetime.strptime(x,'%Y-%m-%dT%H:%M:%S'),
                "default": None,
                "location" : "form"
            }
        }
        
        args = self.validate(rules)
        
        Search(**args).save(self.publish)
        
        return {
            "ok" : "Search Request generated"
        }, 201
        
    def get(self):
        rules = {
            "user" : {
                "type" : int,
                "location" : "args",
                "default": None,
                "help" : "Il campo 'user' risulta essere obbligatorio, ma non è stato passato."
            },
            "text" : {
                "type" : str,
                "location" : "args",
                "default": None,
                "help" : "Il campo 'text' risulta essere obbligatorio, ma non è stato passato."
            }
        }
        
        args = self.validate(rules)
        
        flts = {}
        
        for key in rules.keys():
            if args[key] is not None:
                flts[key] = args[key]
                
        dto = SearchDTO()        
        
        return [dto.build(**search) for search in Search.getAll(flts)];                