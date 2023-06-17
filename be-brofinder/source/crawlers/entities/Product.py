from typing import List

from source.crawlers.entities.Review import Review

class Product:
    def __init__(self,
            name: str, 
            price: float, 
            description: str, 
            reviews: List[Review],
            url : str
        ) -> None:

        self.name = name
        self.price = price
        self.descript = description
        self.reviews = reviews
        
        self.url = url