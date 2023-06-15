from typing import List

from source.crawlers.entities.Review import Review

class Product:
    def __init__(self,
            name: str, 
            price: str, 
            descript: str, 
            reviews: dict[Review],
            url : str
        ) -> None:

        self.name = name
        self.price = price
        self.descript = descript
        self.reviews = reviews
        
        self.url = url