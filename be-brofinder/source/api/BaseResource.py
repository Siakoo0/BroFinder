from flask_restful import Resource

from flask_restful import reqparse

class BaseResource(Resource):
    __name__ = "NoName"

    @property
    def urls(self):
        return ()
    
    def __getParser(self, rules : dict):
        parser = reqparse.RequestParser()

        for field, rule in rules.items():
            parser.add_argument(field, **rule)

        return parser

    def validate(self, rules : dict):
        return self.__getParser(rules).parse_args()