from json import loads, dumps

class EntityDTO:
    def __init__(self, params) -> None:
        self.params = params
        
    def build(self, **data):
        data_dict = {}
        
        for param in self.params:
            if param in data:
                data_dict[param] = data.get(param, "")
                
        return loads(dumps(data_dict, default=str))