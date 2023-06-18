from typing import List

from source.crawlers.entities.Review import Review
from source.crawlers.entities.Entity import Entity

from bson.objectid import ObjectId

from source.utils.MongoDB import MongoDB

from datetime import datetime, timedelta

class Product(Entity):
    
    def collection():
        return "products"

    def __init__(self,
            name: str, 
            price: float, 
            description: str, 
            url : str,
            reviews: List[Review] = [],
            images : List[str] = [],
            _id=ObjectId(),
            reviews_summary = "",
            created_at=datetime.now()
        ) -> None:

        self._id = _id
        self.name = name
        self.price = price
        self.description = description
        self.reviews = reviews
        self.images = images
        self.url = url
        self.created_at = created_at
        self.reviews_summary = reviews_summary

        self.save()

    @staticmethod
    def find(url : str):
        product = list(MongoDB().collection("products").find({"url": url}))
        if len(product) > 0:
            product = product[0]["data"][-1]
            return Product(**product)
        return None
    
    def isExpired(self, minutes=3) -> bool:
        now = datetime.now()
        return now - self.created_at > timedelta(minutes=minutes)

    def save(self):
        entity = {}

        for k, v in self.__dict__.items():
            if isinstance(v, list):
                entity[k] = list(map(self.convert, v))
            else:    
                entity[k] = self.convert(v)

        saved_entity = list(MongoDB().collection("products").find({"url": self.url}))

        if len(saved_entity):
            saved_entity = saved_entity[0]
            saved_entity["last_fetch"] = datetime.now()
            saved_entity["data"].append(entity)

            MongoDB().collection("products").update_one(
                {"_id": saved_entity["_id"]}, 
                {"$set" : saved_entity}
            )
        else:
            MongoDB().collection("products").insert_one({
                "url" : entity["url"],
                "last_fetch" : datetime.now(),
                "data" : [entity]
            })