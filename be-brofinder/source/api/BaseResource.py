from flask_restful import Resource, reqparse

from source.database.mongodb.MongoDB import MongoDB

class BaseResource(Resource):
    
    def __init__(self, **kwargs) -> None:
        if "queues" in kwargs.keys(): self.setQueue(kwargs["queues"])
    
    @property
    def mongo(self):
        return MongoDB()
    
    @property
    def urls(self):
        return ()
    
    def setQueue(self, queue):
        self.queues = queue        
        
    def __getParser(self, rules : dict):
        parser = reqparse.RequestParser(bundle_errors=True)

        for field, rule in rules.items():
            parser.add_argument(field, **rule)

        return parser

    def validate(self, rules : dict):
        return self.__getParser(rules).parse_args()