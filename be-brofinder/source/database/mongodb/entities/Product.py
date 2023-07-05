from typing import List

from source.database.mongodb.entities.Review import Review
from source.database.mongodb.entities.Entity import Entity

from bson.objectid import ObjectId

from source.database.mongodb.MongoDB import MongoDB

from datetime import datetime, timedelta

# TODO: Passare in un file configurabile
class ProductParams:
    EXPIRATION_TIME=15

class Product(Entity):

    def __init__(self,
            name: str,
            price: float,
            description: str,
            url : str,
            reviews: List[Review] = [],
            images : List[str] = [],
            _id = None,
            reviews_summary = "",
            keyword="",
            scheduled_fetch=False,
            created_at=None
        ) -> None:
      
        super().__init__(_id if _id is not None else ObjectId())

        self.name = name
        self.price = price
        self.description = description
        self.reviews = reviews
        self.images = images
        self.url = url
        if created_at is None: self.created_at = datetime.now()
        else: self.created_at = created_at
        self.reviews_summary = reviews_summary
        self.keyword=keyword
        self.scheduled_fetch=scheduled_fetch

    @classmethod
    def collection(self):
        return "products"

    @classmethod
    def get(self, url : str):
        product = super().find({"url" : url})

        if product is not None:
            return Product(**product)
        return None

    def isExpired(self, minutes=ProductParams.EXPIRATION_TIME) -> bool:
        now = datetime.now()
        return now - self.created_at > timedelta(minutes=minutes)

    def save(self):
        entity = self.convert()
        super().save(entity)

        # saved_entity = self.find({"url": self.url})

        # if saved_entity is not None:
        #     saved_entity["data"].append(entity)
        #     saved_entity["scheduled_fetch"] = False
        #     self.update(saved_entity)
        # else:
        #     super().save({
        #         "url" : entity["url"],
        #         "data" : [entity]
        #     })