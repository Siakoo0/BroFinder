from datetime import datetime
from redis import Redis
from json import loads, dumps
from dataclasses import dataclass

from bson.objectid import ObjectId

from source.api.BaseResource import BaseResource

from source.database.mongodb.entities.Product import Product

from source.api.dto.ProductDTO import ProductDTO

        
class ProductResource(BaseResource):
    @property
    def urls(self):
        return ('/api/product/<string:prod_id>', )
    
    def get(self, prod_id):
        product = Product.find_by_id(prod_id)
        dto = ProductDTO()
                
        return dto.build(**product)
    