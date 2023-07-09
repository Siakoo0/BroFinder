from datetime import datetime
from redis import Redis
from json import loads, dumps
from dataclasses import dataclass

from bson.objectid import ObjectId

from source.api.BaseResource import BaseResource

from source.database.mongodb.entities.Product import Product

from source.api.dto.ProductDTO import ProductDTO

        
class ProductListResource(BaseResource):
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
            },
            "page" : {
                "type" : int,
                "default" : 0,
                "location" : "args"
            },
            "size" : {
                "type" : int,
                "default" : 50,
                "location" : "args"
            }
        }


        args = self.validate(rules)

        start_offset = args["page"] * args["size"]
        end_offset = (args["page"] + 1) * args["size"]

        text = args["text"].lower()
        
        filters = {
            "url" : {"url" :  text},
            "name" : {"name" :  {"$regex" : f'.*{text}.*'}},
            "keyword" : {"keyword": {"$regex" : f'.*{text}.*'}},
        }

        filters_args = args["filter"].split(",")

        if "id" in filters_args: filters["id"] = {"_id" : ObjectId(text)}

        or_cond = [filters[filt] for filt in filters_args if filt in filters.keys()]

        filts = {}
        
        if len(or_cond) > 0:
            filts["$or"] = or_cond

        if args["price"] > 0:
            filts["price"] = {"$lte" : args['price']}


        products = Product.getAll(filts)
        count_prod = len(products)
        products = products[start_offset : end_offset]
        
        dto = ProductDTO()
        
        serializer = lambda product: dto.build(**product)
        
        return {
            "total" : count_prod,
            "data" : list(map(serializer, products))
        }, 200