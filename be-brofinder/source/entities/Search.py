from source.entities.Entity import Entity

from bson.objectid import ObjectId
from datetime import datetime



class Search(Entity):
    @classmethod
    def collection(self):
        return ("search")
    
    def __init__(self, 
                text : str, 
                user : int, 
                _id = ObjectId(), 
                forward:bool=False, 
                price : float=None, 
                publish_at:datetime=None,
        ) -> None:
        
        super().__init__(_id)
        
        self.text = text
        self.forward = forward

        self.user = user
        self.price = price
        self.publish_at = publish_at
        
        self.last_forwarded = None
            
    def exists(self):
        # Controllo se la ricerca risulta essere già effettuata
        saved_entity = self.find({"text" : self.text, "user" : self.user})
        return saved_entity is not None
    
    @classmethod
    def get(self, text, user):
        search = self.find({"text" : text, "user" : user})
        if search is not None:
            del search["updated_at"]
            return Search(**search)

        return None
    
    def update(self, **search_param):
        if not self.exists(): return
        
        expect_params = ["price", "publish_at", "forward"]
        data = {}
        
        for param in expect_params:
            if param in search_param.keys() and search_param[param] is not None:
                data[param] = search_param[param]

        item = self.find({'text' : self.text, "user" : self.user})
        item = item | data
        
        print(item)
        super().update(item)        
        
    def save(self, cb_fn = None):
        # Se la ricerca già esiste, non va salvata ma dovrà essere aggiornata
        if self.exists(): return
        
            
        search_record = {
            "user" : self.user,
            "forward" : self.forward
        }
        
        opt_fields = {
            "price" : self.price,
            "publish_at" : self.publish_at
        }

        for field, value in opt_fields.items():
            if value is not None:
                search_record[field] = value
                
        data = {
            "text" : self.text
        } | search_record

        super().save(data)
        
        if cb_fn is not None:
            cb_fn(data)