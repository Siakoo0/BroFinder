from datetime import datetime
from redis import Redis
from json import dumps, loads

from source.api.BaseResource import BaseResource
from source.api.dto.SearchDTO import SearchDTO


from source.database.mongodb.entities.Search import Search

from flask_restful import inputs


class SearchListResource(BaseResource):
    @property
    def urls(self):
        return ('/api/search', )
    
    def enqueue(self, data):
        data["text"] = data["text"].lower()
        self.queues["crawler/search_queue"].put(data)

    def put(self):
        rules = {
            "text" : {
                "type" : str,
                "required" : True,
                "location" : "json",
                "help" : "Il campo 'text' risulta essere obbligatorio, ma non è stato passato."
            },
            "user" : {
                "type" : int,
                "required" : True,
                "location" : "json",
                "help" : "Il campo 'user' risulta essere obbligatorio, ma non è stato passato."
            },
            "forward" : {
                "type" : bool,
                "default" : False,
                "location" : "json",
                "help" : "Il campo 'user' risulta essere obbligatorio, ma non è stato passato."
            }
        }

        args = self.validate(rules)

        search : Search = Search.get(text=args['text'], user=args['user'])
        search.update(forward=args["forward"])

        dto = search.convert()
        dto["forward"] = args["forward"]

        return SearchDTO().build(**dto)

    def post(self):
        rules = {
            "text" : {
                "type" : str,
                "required" : True,
                "location" : "json",
                "help" : "Il campo 'text' risulta essere obbligatorio, ma non è stato passato."
            },
            "price" : {
                "type" : int,
                "default": None,
                "location" : "json"
            },
            "user" : {
                "type" : int,
                "required" : True,
                "location" : "json",
                "help" : "Il campo 'user' risulta essere obbligatorio, ma non è stato passato."
            },
            "forward" : {
                "type" : inputs.boolean,
                "default": False,
                "location" : "json"
            },
            "publish_at": {
                "type" : lambda x: datetime.strptime(x,'%Y-%m-%dT%H:%M:%S'),
                "default": None,
                "location" : "json"
            }
        }
        
        args = self.validate(rules)
        
        Search(**args).save(self.enqueue)
        
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