from abc import ABC, abstractmethod
from typing import List

from source.crawler.entities.Product import Product
from source.crawler.helpers.Singleton import Singleton

class Scraper(ABC):
    @abstractmethod
    def search(self, product: str) -> List[Product]:
        pass
