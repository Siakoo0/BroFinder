from typing import List

from source.database.mongodb.entities.Review import Review
from source.database.mongodb.entities.Entity import Entity

from bson.objectid import ObjectId

from source.database.mongodb.MongoDB import MongoDB

from datetime import datetime, timedelta

class Product(Entity):

    def __init__(self,
            name: str,
            price: float,
            description: str,
            url : str,
            reviews: List[Review] = [],
            images : List[str] = [],
            _id=ObjectId(),
            reviews_summary = "",
            created_at=datetime.now(),
            keyword=""
        ) -> None:
        
        super().__init__(_id)

        self.name = name
        self.price = price
        self.description = description
        self.reviews = reviews
        self.images = images
        self.url = url
        self.created_at = created_at
        self.reviews_summary = reviews_summary
        self.keyword=keyword

    @classmethod
    def collection(self):
        return "products"

    @classmethod
    def get(self, url : str):
        product = super().find({"url" : url})
        
        if product is not None:
            product["data"][-1]["_id"] = product["_id"]
            product = product["data"][-1]
            
            return Product(**product)
        
        return None

    def isExpired(self, minutes=3) -> bool:
        now = datetime.now()
        return now - self.created_at > timedelta(minutes=minutes)

    def save(self):
        entity = self.convert()

        saved_entity = self.find({"url": self.url})

        if saved_entity is not None:
            saved_entity["data"].append(entity)
            self.update(saved_entity)
        else:
            super().save({
                "url" : entity["url"],
                "data" : [entity]
            })