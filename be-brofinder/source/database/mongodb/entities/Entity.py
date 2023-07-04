from abc import ABC, abstractclassmethod, abstractmethod
from bson.objectid import ObjectId
from datetime import datetime

from source.database.mongodb.MongoDB import MongoDB


class Entity(ABC):
    
    def __init__(self, _id=ObjectId()) -> None:
        self._id = _id
    
    @abstractclassmethod
    def collection(self):
        pass
    
    def convert_elem(self, elem):
        if hasattr(elem, "__dict__"):
            return elem.__dict__
        else:
            return elem

    def convert(self):
        entity = {}
        
        for k, v in self.__dict__.items():
            if isinstance(v, list):
                entity[k] = list(map(self.convert_elem, v))
            else:
                entity[k] = self.convert_elem(v)

        return entity
        
    @classmethod
    def find(self, params):
        entity = self.getAll(params)
        if len(entity) > 0:
            return entity[0]
        return None

    @classmethod
    def getAll(self, params):
        entities = MongoDB().collection(self.collection()).find(params)
        return list(entities)

    def update(self,  new_entity, search_param = {}):
        if len(search_param.keys()) == 0:
            search_param["_id"] = new_entity["_id"]
            
        saved_entity = self.find(search_param)
            
        if saved_entity is not None:
            new_entity["updated_at"] = datetime.now()
            del new_entity["_id"]
            
            # Il prodotto è stato aggiornato
            if "scheduled_update" in new_entity.keys():
                del new_entity["scheduled_update"];
                
            MongoDB().collection(self.collection()).replace_one(
                search_param, new_entity
            )
      
    def get(self):
        pass
            
    def save(self, entity):
        entity["updated_at"] = datetime.now()
        MongoDB().collection(self.collection()).insert_one(entity)