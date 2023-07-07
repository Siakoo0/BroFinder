from datetime import datetime
from redis import Redis
from json import loads, dumps
from dataclasses import dataclass

from source.api.BaseResource import BaseResource

from source.database.mongodb.entities.Product import Product

from source.api.dto.ProductDTO import ProductDTO

        
class ProductResource(BaseResource):
    @property
    def urls(self):
        return ('/api/product', )
    
    def get(self):
        rules = {
            "text" : {
                "type" : str,
                "required" : True,
                "location" : "args",
                "help" : "Il campo 'text' risulta essere obbligatorio, ma non è stato passato."
            },
            "filter" : {
                "type" : str,
                "default" : "keyword",
                "location" : "args",
                "help" : "Il campo 'filter' risulta essere obbligatorio, ma non è stato passato.",
            },
            "price" : {
                "type" : int,
                "default": 0,
                "location" : "args"
            }
        }


        args = self.validate(rules)

        text = args["text"]
        
        filters = {
            "url" : {"url" :  text},
            "name" : {"name" :  {"$regex" : f'.*{text}.*'}},
            "keyword" : {"keyword": {"$regex" : f'.*{text}.*'}}
        }

        or_cond = [filters[filt] for filt in args["filter"].split(",") if filt in filters.keys()]

        filts = {}
        
        if len(or_cond) > 0:
            filts["$or"] = or_cond

        if args["price"] > 0:
            filts["price"] = {"$lte" : args['price']}

        products = Product.getAll(filts)
        
        dto = ProductDTO()
        
        serializer = lambda product: dto.build(**product)
        
        return list(map(serializer, products)), 200